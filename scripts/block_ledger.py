#!/usr/bin/env python3
"""Persist solo-found coinbase blocks and track confirmations/maturity from the chain."""
import json, os, re, time
from pathlib import Path
from datetime import datetime, timezone

DATADIR = Path(os.getenv("FIX_DATADIR", "/data/fixedcoin"))
LEDGER = Path(os.getenv("BLOCK_LEDGER_PATH", str(DATADIR / "solo-blocks.json")))
PAYOUT_FILE = DATADIR / "payout_address"
EVENTS_PATH = Path(os.getenv("STRATUM_EVENTS_PATH", "/app/data/events.jsonl"))
STATS_PATH = Path(os.getenv("STRATUM_STATS_PATH", "/app/data/stats.json"))
USER = os.getenv("FIX_RPCUSER", "fixrpc")
PASS = os.getenv("FIX_RPCPASS", "")
PORT = int(os.getenv("FIX_RPCPORT", "24761"))
PAYOUT_ADDRESS = os.getenv("FIX_PAYOUT_ADDRESS", "").strip()
MATURITY = int(os.getenv("COINBASE_MATURITY", "100"))
POLL = float(os.getenv("BLOCK_LEDGER_POLL", "2"))
SCAN_BACK = max(1, int(os.getenv("BLOCK_LEDGER_SCAN_BACK", "144")))
EVENT_SCAN_LINES = max(100, int(os.getenv("BLOCK_LEDGER_EVENT_SCAN_LINES", "10000")))


def resolve_payout_address():
    if PAYOUT_ADDRESS:
        return PAYOUT_ADDRESS
    try:
        saved = PAYOUT_FILE.read_text(errors="ignore").strip()
        if saved:
            return saved
    except OSError:
        pass
    try:
        cfg = Path("/app/config/config.yaml")
        if cfg.exists():
            import yaml
            data = yaml.safe_load(cfg.read_text()) or {}
            address = str((data.get("pool") or {}).get("payout_address") or "").strip()
            if address:
                return address
    except Exception:
        pass
    return ""


def rpc(method, params=None):
    import requests
    from requests.auth import HTTPBasicAuth
    endpoint = f"http://127.0.0.1:{PORT}"
    response = requests.post(
        endpoint,
        json={"jsonrpc": "1.0", "id": "block-ledger", "method": method, "params": params or []},
        auth=HTTPBasicAuth(USER, PASS),
        timeout=30,
    )
    try:
        data = response.json()
    except ValueError:
        raise RuntimeError(f"{method}: HTTP {response.status_code}: {response.text[:500]}")
    if data.get("error"):
        raise RuntimeError(f"{method}: {data['error']}")
    if response.status_code >= 400:
        raise RuntimeError(f"{method}: HTTP {response.status_code}: {data}")
    return data.get("result")


def load():
    try:
        data = json.loads(LEDGER.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save(rows):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    tmp = LEDGER.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, LEDGER)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def payout_script_hex(payout_address):
    if not payout_address:
        return ""
    try:
        info = rpc("validateaddress", [payout_address]) or {}
        return str(info.get("scriptPubKey") or "").lower()
    except Exception:
        return ""


def payout_matches(vout, payout_address, target_script_hex=""):
    if not payout_address:
        return False
    spk = vout.get("scriptPubKey") or {}
    target = str(target_script_hex or "").lower()
    actual = str(spk.get("hex") or "").lower()
    if target and actual and target == actual:
        return True
    addresses = spk.get("addresses") or []
    if payout_address in addresses:
        return True
    return spk.get("address") == payout_address


def accepted_heights_from_sources():
    heights = set()
    try:
        lines = EVENTS_PATH.read_text(errors="ignore").splitlines()[-EVENT_SCAN_LINES:]
    except OSError:
        lines = []
    for line in lines:
        try:
            row = json.loads(line)
            msg = str(row.get("msg") or "")
        except Exception:
            msg = line
        if "BLOCK ACCEPTED" not in msg:
            continue
        match = re.search(r"height=(\d+)", msg)
        if match:
            heights.add(int(match.group(1)))

    try:
        stats = json.loads(STATS_PATH.read_text())
    except Exception:
        stats = {}
    for row in stats.get("blocks_log", []) if isinstance(stats, dict) else []:
        if isinstance(row, dict):
            try:
                height = int(row.get("height") or 0)
            except Exception:
                height = 0
            if height > 0:
                heights.add(height)
    return heights


def find_solo_block(height, payout_address, target_script_hex="", accepted=False):
    try:
        blockhash = str(rpc("getblockhash", [height]) or "")
        if not blockhash:
            return None
        block = rpc("getblock", [blockhash, 1]) or {}
    except Exception:
        return None

    txids = block.get("tx") or []
    if not txids:
        return None

    first = txids[0]
    try:
        coinbase = first if isinstance(first, dict) else (rpc("getrawtransaction", [str(first), 1, blockhash]) or {})
    except Exception:
        return None
    if not isinstance(coinbase, dict):
        return None
    vin = coinbase.get("vin") or []
    if not vin or not vin[0].get("coinbase"):
        return None

    vouts = coinbase.get("vout") or []
    total_reward = sum(float(v.get("value") or 0) for v in vouts)
    payout_reward = sum(
        float(v.get("value") or 0)
        for v in vouts
        if payout_matches(v, payout_address, target_script_hex)
    )

    # A block explicitly reported as accepted by our Stratum server is ours,
    # even if address decoding differs between daemon versions. For ordinary
    # background scans, require an actual payout match so unrelated chain blocks
    # never enter the solo ledger.
    if accepted:
        if total_reward <= 0:
            return None
        reward = payout_reward if payout_reward > 0 else total_reward
    else:
        if payout_reward <= 0:
            return None
        reward = payout_reward

    block_time = int(block.get("time") or coinbase.get("blocktime") or 0)
    found_at = datetime.fromtimestamp(block_time, timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if block_time else now()
    return {
        "txid": str(coinbase.get("txid") or first or ""),
        "blockhash": blockhash,
        "height": int(height),
        "reward": reward,
        "coinbase_reward": total_reward,
        "payout_reward": payout_reward,
        "found_at": found_at,
        "maturity_height": int(height) + MATURITY,
        "maturity": MATURITY,
    }


def sync():
    rows = load()
    if not LEDGER.exists():
        save(rows)

    payout_address = resolve_payout_address()
    if not payout_address:
        raise RuntimeError("payout address is not available yet")
    target_script_hex = payout_script_hex(payout_address)

    chain = rpc("getblockchaininfo") or {}
    tip = int(chain.get("blocks") or 0)
    if tip <= 0:
        return len(rows), tip

    accepted_heights = accepted_heights_from_sources()
    by_key = {
        (str(x.get("blockhash") or ""), int(x.get("height") or 0)): x
        for x in rows
        if isinstance(x, dict)
    }

    heights = set(range(max(0, tip - SCAN_BACK + 1), tip + 1))
    heights.update(h for h in accepted_heights if 0 <= h <= tip)

    for height in sorted(heights):
        found = find_solo_block(
            height,
            payout_address,
            target_script_hex,
            accepted=(height in accepted_heights),
        )
        if not found:
            continue
        key = (found["blockhash"], found["height"])
        row = by_key.get(key)
        if row is None:
            found["last_seen"] = now()
            by_key[key] = found
            print(
                f"[block-ledger] SOLO BLOCK height={found['height']} "
                f"hash={found['blockhash']} txid={found['txid']} "
                f"reward={found['reward']:.8f} payout={found['payout_reward']:.8f}",
                flush=True,
            )
        else:
            row["last_seen"] = now()
            row["reward"] = found["reward"]
            row["coinbase_reward"] = found["coinbase_reward"]
            row["payout_reward"] = found["payout_reward"]
            row["txid"] = found["txid"]
            row["found_at"] = row.get("found_at") or found["found_at"]

    rows = list(by_key.values())
    for row in rows:
        height = int(row.get("height") or 0)
        blockhash = str(row.get("blockhash") or "")
        confirmations = max(0, tip - height + 1) if height else 0
        remaining = max(0, height + MATURITY - tip) if height else MATURITY
        row["confirmations"] = confirmations
        row["validity_rounds"] = confirmations
        row["validity_target"] = MATURITY
        row["maturity_remaining"] = remaining
        row["mature"] = confirmations >= MATURITY

        canonical = ""
        if height:
            try:
                canonical = str(rpc("getblockhash", [height]) or "")
            except Exception:
                pass
        if blockhash and canonical and canonical != blockhash:
            row["orphaned"] = True
            row["status"] = "ORPHANED"
        else:
            row["orphaned"] = False
            row["status"] = "MATURED" if row["mature"] else "IMMATURE"

    rows.sort(key=lambda x: (int(x.get("height") or 0), str(x.get("found_at") or "")), reverse=True)
    save(rows)
    return len(rows), tip


def main():
    if not LEDGER.exists():
        save([])
    address = resolve_payout_address()
    print(f"[block-ledger] startup rpc=127.0.0.1:{PORT} payout={address or '<missing>'}", flush=True)
    try:
        info = rpc("getblockchaininfo") or {}
        print(f"[block-ledger] RPC OK tip={info.get('blocks')}", flush=True)
    except Exception as exc:
        print(f"[block-ledger] FATAL RPC startup check failed: {exc}", flush=True)
        raise

    while True:
        try:
            count, tip = sync()
            print(f"[block-ledger] blocks={count} tip={tip}", flush=True)
        except Exception as exc:
            print(f"[block-ledger] sync error: {exc}", flush=True)
        time.sleep(POLL)


if __name__ == "__main__":
    main()
