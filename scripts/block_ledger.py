#!/usr/bin/env python3
"""Persist every wallet-generated solo block and track confirmations/maturity."""
import json, os, subprocess, time
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote
import requests
from requests.auth import HTTPBasicAuth

DATADIR = Path(os.getenv("FIX_DATADIR", "/data/fixedcoin"))
LEDGER = Path(os.getenv("BLOCK_LEDGER_PATH", str(DATADIR / "solo-blocks.json")))
USER = os.getenv("FIX_RPCUSER", "fixrpc")
PASS = os.getenv("FIX_RPCPASS", "")
PORT = int(os.getenv("FIX_RPCPORT", "24761"))
WALLET = os.getenv("FIX_WALLET_NAME", "mining")
MATURITY = int(os.getenv("COINBASE_MATURITY", "100"))
POLL = float(os.getenv("BLOCK_LEDGER_POLL", "2"))
CLI = os.getenv("FIXCOIN_CLI", "fixedcoin-cli")


def rpc(method, params=None, wallet=None):
    """Call Core RPC. Wallet RPCs use fixedcoin-cli -rpcwallet for maximum compatibility."""
    if wallet:
        cmd = [CLI, f"-datadir={DATADIR}", f"-rpcwallet={WALLET}", method]
        for value in (params or []):
            cmd.append(json.dumps(value, separators=(",", ":")) if isinstance(value, (dict, list, bool)) else str(value))
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"{method}: fixedcoin-cli exit {proc.returncode}")
        try:
            return json.loads(proc.stdout)
        except ValueError as exc:
            raise RuntimeError(f"{method}: invalid CLI JSON: {proc.stdout[:500]}") from exc

    endpoint = f"http://127.0.0.1:{PORT}"
    response = requests.post(
        endpoint,
        json={"jsonrpc": "1.0", "id": "ledger", "method": method, "params": params or []},
        auth=HTTPBasicAuth(USER, PASS),
        timeout=15,
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


def load():
    try:
        data = json.loads(LEDGER.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save(rows):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    tmp = LEDGER.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    os.replace(tmp, LEDGER)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def sync():
    rows = load()
    if not LEDGER.exists():
        save(rows)

    chain = rpc("getblockchaininfo") or {}
    tip = int(chain.get("blocks") or 0)

    # IMPORTANT: listtransactions is wallet-scoped. FixedCoin's wallet RPC
    # endpoint is inconsistent in some builds, while the CLI's -rpcwallet
    # selector is reliable and is also the documented wallet selection method.
    txs = rpc("listtransactions", ["*", 1000, 0, True], wallet=WALLET) or []

    by_key = {(str(x.get("txid") or ""), int(x.get("height") or 0)): x for x in rows}
    for tx in txs:
        category = str(tx.get("category") or "").lower()
        if category not in {"generate", "immature", "orphan"} and not tx.get("generated"):
            continue

        txid = str(tx.get("txid") or "")
        blockhash = str(tx.get("blockhash") or "")
        if not txid and not blockhash:
            continue

        height = int(tx.get("blockheight") or tx.get("height") or 0)
        if not height and blockhash:
            try:
                height = int((rpc("getblock", [blockhash, 1]) or {}).get("height") or 0)
            except Exception:
                continue
        if height <= 0:
            continue

        key = (txid, height)
        row = by_key.get(key) or {
            "txid": txid,
            "blockhash": blockhash,
            "height": height,
            "reward": abs(float(tx.get("amount") or 0)),
            "found_at": now(),
            "maturity_height": height + MATURITY,
            "maturity": MATURITY,
        }
        if blockhash:
            row["blockhash"] = blockhash
        row["reward"] = abs(float(tx.get("amount") or row.get("reward") or 0))
        row["maturity_height"] = height + MATURITY
        row["last_seen"] = now()
        by_key[key] = row

    rows = list(by_key.values())
    for row in rows:
        h = int(row.get("height") or 0)
        bh = str(row.get("blockhash") or "")
        row["confirmations"] = max(0, tip - h + 1) if h else 0
        row["maturity_remaining"] = max(0, h + MATURITY - tip) if h else MATURITY
        row["mature"] = bool(row["confirmations"] >= MATURITY)
        row["status"] = "ORPHANED" if row.get("orphaned") else ("MATURED" if row["mature"] else "IMMATURE")

        if bh:
            try:
                canonical = str(rpc("getblockhash", [h]) or "")
                if canonical and canonical != bh:
                    row["orphaned"] = True
                    row["status"] = "ORPHANED"
                elif row.get("orphaned") and canonical == bh:
                    row["orphaned"] = False
            except Exception:
                pass

    rows.sort(key=lambda x: (int(x.get("height") or 0), str(x.get("found_at") or "")), reverse=True)
    save(rows)
    return len(rows), tip


def main():
    if not LEDGER.exists():
        save([])

    while True:
        try:
            count, tip = sync()
            print(f"[block-ledger] blocks={count} tip={tip}", flush=True)
        except Exception as exc:
            print(f"[block-ledger] RPC/sync error: {exc}", flush=True)
        time.sleep(POLL)


if __name__ == "__main__":
    main()
