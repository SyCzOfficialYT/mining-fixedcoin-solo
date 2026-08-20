#!/usr/bin/env python3
"""Persist solo-found coinbase blocks and track confirmations/maturity from the chain."""
import json, os, subprocess, time
from pathlib import Path
from datetime import datetime, timezone

DATADIR = Path(os.getenv("FIX_DATADIR", "/data/fixedcoin"))
LEDGER = Path(os.getenv("BLOCK_LEDGER_PATH", str(DATADIR / "solo-blocks.json")))
USER = os.getenv("FIX_RPCUSER", "fixrpc")
PASS = os.getenv("FIX_RPCPASS", "")
PORT = int(os.getenv("FIX_RPCPORT", "24761"))
WALLET = os.getenv("FIX_WALLET_NAME", "mining")
PAYOUT_ADDRESS = os.getenv("FIX_PAYOUT_ADDRESS", "").strip()
MATURITY = int(os.getenv("COINBASE_MATURITY", "100"))
POLL = float(os.getenv("BLOCK_LEDGER_POLL", "2"))
SCAN_BACK = max(1, int(os.getenv("BLOCK_LEDGER_SCAN_BACK", "12")))
CLI = os.getenv("FIXCOIN_CLI", "fixedcoin-cli")


def rpc(method, params=None):
    """Use the node RPC directly; wallet RPCs are deliberately not required."""
    import requests
    from requests.auth import HTTPBasicAuth

    endpoint = f"http://127.0.0.1:{PORT}"
    response = requests.post(
        endpoint,
        json={"jsonrpc": "1.0", "id": "ledger", "method": method, "params": params or []},
        auth=HTTPBasicAuth(USER, PASS),
        timeout=20,
    )
    try:
        data = response.json()
    except ValueError:
        response.raise_for_status()
        raise RuntimeError(f"{method}: RPC returned non-JSON HTTP {response.status_code}")
    if data.get("error"):
        raise RuntimeError(data["error"])
    if response.status_code >= 400:
        raise RuntimeError(f"{method}: HTTP {response.status_code}: {data}")
    return data.get("result")


def cli(method, *params):
    """Call fixedcoin-cli for RPCs where the HTTP RPC is not reliable."""
    cmd = [CLI, f"-datadir={DATADIR}", method]
    cmd.extend(str(x) for x in params)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"{method}: cli exit {proc.returncode}")
    try:
        return json.loads(proc.stdout)
    except ValueError as exc:
        raise RuntimeError(f"{method}: invalid CLI JSON: {proc.stdout[:500]}") from exc


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


def payout_matches(vout):
    """Return true when a coinbase output pays our configured solo address."""
    if not PAYOUT_ADDRESS:
        return False
    spk = vout.get("scriptPubKey") or {}
    addresses = spk.get("addresses") or []
    if PAYOUT_ADDRESS in addresses:
        return True
    # Some Core versions expose a single address rather than addresses[].
    return spk.get("address") == PAYOUT_ADDRESS


def find_solo_block(height):
    """Inspect the canonical block at height and recognize our coinbase payout.

    This intentionally does NOT use listtransactions/getwalletinfo. A solo pool
    can find a block even when the wallet RPC has no transaction history yet.
    """
    try:
        blockhash = cli("getblockhash", height)
        block = cli("getblock", blockhash, 2)
    except Exception:
        return None

    txs = block.get("tx") or []
    if not txs:
        return None
    coinbase = txs[0]
    if not coinbase.get("vin") or not coinbase["vin"][0].get("coinbase"):
        return None

    outputs = coinbase.get("vout") or []
    reward = sum(float(v.get("value") or 0) for v in outputs if payout_matches(v))
    if reward <= 0:
        return None

    return {
        "txid": str(coinbase.get("txid") or ""),
        "blockhash": str(blockhash),
        "height": int(height),
        "reward": reward,
        "found_at": now(),
        "maturity_height": int(height) + MATURITY,
        "maturity": MATURITY,
    }


def sync():
    rows = load()
    if not LEDGER.exists():
        save(rows)

    chain = cli("getblockchaininfo") or {}
    tip = int(chain.get("blocks") or 0)
    if tip <= 0:
        return len(rows), tip

    by_key = {
        (str(x.get("blockhash") or ""), int(x.get("height") or 0)): x
        for x in rows
    }

    # Scan the newest blocks every cycle. This catches a newly submitted block
    # without depending on wallet notifications and also survives a ledger
    # process restart. The small overlap protects against a short reorg.
    start = max(0, tip - SCAN_BACK + 1)
    for height in range(start, tip + 1):
        found = find_solo_block(height)
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
                f"reward={found['reward']:.8f}",
                flush=True,
            )
        else:
            row["last_seen"] = now()
            row["reward"] = found["reward"]
            row["txid"] = found["txid"]

    rows = list(by_key.values())
    for row in rows:
        h = int(row.get("height") or 0)
        bh = str(row.get("blockhash") or "")
        confirmations = max(0, tip - h + 1) if h else 0
        remaining = max(0, h + MATURITY - tip) if h else MATURITY

        row["confirmations"] = confirmations
        row["maturity_remaining"] = remaining
        row["mature"] = confirmations >= MATURITY

        # Re-check canonicality for every stored block. A stale/reorged block
        # must never remain confirmed in the dashboard.
        canonical = ""
        if h:
            try:
                canonical = str(cli("getblockhash", h) or "")
            except Exception:
                canonical = ""

        if bh and canonical and canonical != bh:
            row["orphaned"] = True
            row["status"] = "ORPHANED"
        else:
            row["orphaned"] = False
            row["status"] = "MATURED" if row["mature"] else "IMMATURE"

    rows.sort(key=lambda x: (int(x.get("height") or 0), str(x.get("found_at") or "")), reverse=True)
    save(rows)
    return len(rows), tip


def main():
    save(load()) if not LEDGER.exists() else None
    if not PAYOUT_ADDRESS:
        print("[block-ledger] WARNING: FIX_PAYOUT_ADDRESS is empty; solo block detection is disabled", flush=True)

    while True:
        try:
            count, tip = sync()
            print(f"[block-ledger] blocks={count} tip={tip}", flush=True)
        except Exception as exc:
            print(f"[block-ledger] RPC/sync error: {exc}", flush=True)
        time.sleep(POLL)


if __name__ == "__main__":
    main()
