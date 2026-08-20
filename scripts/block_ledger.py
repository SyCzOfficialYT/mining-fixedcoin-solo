#!/usr/bin/env python3
"""Persist every wallet-generated solo block and track confirmations/maturity.

The ledger is append-only from the pool's perspective: records are never removed.
A block can transition VALID -> ORPHANED after a reorg, but the historical record
remains available for the dashboard.
"""
import json
import os
import time
from pathlib import Path
from datetime import datetime, timezone

import requests
from requests.auth import HTTPBasicAuth

DATADIR = Path(os.getenv("FIX_DATADIR", "/data/fixedcoin"))
DATA = Path("/app/data")
LEDGER = DATA / "blocks.json"
USER = os.getenv("FIX_RPCUSER", "fixrpc")
PASS = os.getenv("FIX_RPCPASS", "")
PORT = int(os.getenv("FIX_RPCPORT", "24761"))
MATURITY = int(os.getenv("COINBASE_MATURITY", "100"))
POLL = float(os.getenv("BLOCK_LEDGER_POLL", "2"))


def rpc(method, params=None):
    r = requests.post(
        f"http://127.0.0.1:{PORT}",
        json={"jsonrpc": "1.0", "id": "ledger", "method": method, "params": params or []},
        auth=HTTPBasicAuth(USER, PASS), timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("result")


def load():
    try:
        data = json.loads(LEDGER.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save(rows):
    tmp = LEDGER.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    os.replace(tmp, LEDGER)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def sync():
    chain = rpc("getblockchaininfo") or {}
    tip = int(chain.get("blocks") or 0)
    txs = rpc("listtransactions", ["*", 1000, 0, True]) or []
    rows = load()
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
                bi = rpc("getblock", [blockhash, 1]) or {}
                height = int(bi.get("height") or 0)
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
    DATA.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            count, tip = sync()
            print(f"[block-ledger] blocks={count} tip={tip}", flush=True)
        except Exception as exc:
            print(f"[block-ledger] RPC/sync error: {exc}", flush=True)
        time.sleep(POLL)


if __name__ == "__main__":
    main()
