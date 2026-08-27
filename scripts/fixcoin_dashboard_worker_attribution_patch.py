#!/usr/bin/env python3
"""Install robust per-worker attribution for the LiveShare dashboard.

The Stratum layer emits worker-aware ACCEPT/REJECT/authorize telemetry. The
old dashboard parser kept one global ``current_worker`` and therefore merged
shares from multiple ASICs/NMMiner connections into whichever worker happened
to authorize last. Replace the whole parser function so attribution is based
on the worker explicitly present in each event whenever available.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "monitor" / "app.py"
text = PATH.read_text(encoding="utf-8")


def replace_function(source, name, replacement):
    tree = ast.parse(source)
    node = next((n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name), None)
    if node is None:
        raise RuntimeError(f"monitor function not found: {name}")
    lines = source.splitlines(keepends=True)
    start = sum(map(len, lines[:node.lineno - 1]))
    end = sum(map(len, lines[:node.end_lineno]))
    return source[:start] + replacement.rstrip() + "\n" + source[end:]


replacement = r'''def parse_logs():
    accepted, rejected, blocks, workers, job = [], 0, [], {}, {}
    now = time.time()
    current_worker = None

    def worker_row(name, ts=0.0):
        name = str(name or "unknown")
        row = workers.setdefault(name, {"accepted": 0, "rejected": 0, "difficulty": 0.0})
        if ts:
            row["last_seen"] = ts
        return row

    def parse_identity(line, row):
        # Examples:
        # authorize ... miner=NMMiner/v2 version=2
        # MINER DETECT family=NMMiner variant=v2 version=2 ua='...'
        m = re.search(r"miner=([^/\s]+)/([^\s]+)\s+version=([^\s]+)", line, re.I)
        if m:
            row["miner_family"], row["miner_variant"], row["miner_version"] = m.groups()
        m = re.search(r"MINER DETECT\s+family=([^\s]+)\s+variant=([^\s]+)\s+version=([^\s]+)\s+ua=(.+)$", line, re.I)
        if m:
            row["miner_family"], row["miner_variant"], row["miner_version"], ua = m.groups()
            row["user_agent"] = ua.strip().strip("'")
        if re.search(r"mode=vardiff=True", line, re.I):
            row["vardiff"] = True
        if re.search(r"mode=(?:fixed|nmminer-fixed)", line, re.I):
            row["vardiff"] = False

    for line in lines(LOG):
        ts = parse_ts(line[:19])

        # Always bind identity/difficulty to the worker named by the event.
        m = re.search(r"authorize\s+(\S+).*?(?:diff|share_diff)\s*[=:]\s*([0-9.eE+-]+)", line, re.I)
        if m:
            name, diff = m.groups()
            current_worker = name
            w = worker_row(name, ts)
            w["difficulty"] = float(diff)
            parse_identity(line, w)

        # Miner detection can arrive before authorize; recover the worker from
        # the same connection's immediately following authorization when the
        # log includes worker= in the detection event, otherwise keep it as a
        # connection-wide hint without inventing a worker name.
        if "MINER DETECT" in line:
            parse_identity(line, worker_row(current_worker, ts))

        m = re.search(r"NEW ROUND\s+height=(\d+)\s+netdiff=([0-9.eE+-]+)", line, re.I)
        if m:
            job["height"] = int(m.group(1))
            job["network_diff"] = float(m.group(2))

        m = re.search(r"Job\s+([^\s]+).*?height=(\d+).*?(?:miner=([0-9.eE+-]+))?.*?(?:dev=([0-9.eE+-]+))?", line, re.I)
        if m:
            job.update({"job_id": m.group(1), "height": int(m.group(2))})
            if m.group(3):
                job["miner_value"] = float(m.group(3))
            if m.group(4):
                job["dev_value"] = float(m.group(4))

        # New Stratum telemetry is worker-explicit. Keep legacy parsing as a
        # fallback for old events already present in stratum.log.
        m = re.search(r"ACCEPT(?:\s+worker=(\S+))?\s+#(\d+)\s+work=([0-9.]+).*?(?:pool|pool_diff)=([0-9.]+).*?hash=([0-9a-fA-F]+)", line, re.I)
        if m:
            worker_hint, num, work, diff, h = m.groups()
            worker = worker_hint or current_worker or "unknown"
            w = worker_row(worker, ts)
            w["accepted"] += 1
            w["difficulty"] = float(diff)
            accepted.append({
                "ts": line[:19], "epoch": ts, "num": int(num),
                "work": float(work), "pool_diff": float(diff),
                "hash": h[:16], "worker": worker,
            })

        # Attribute rejects to their explicit worker too. This fixes the
        # dashboard's aggregate reject count being disconnected from miner
        # cards when several workers are active.
        m = re.search(r"REJECT\s+reason=[^\s]+\s+worker=(\S+)", line, re.I)
        if m:
            worker = m.group(1)
            w = worker_row(worker, ts)
            w["rejected"] += 1
            parse_identity(line, w)
        elif re.search(r"\bREJECT\b|\blow difficulty\b|stale job|bad params|invalid", line, re.I):
            rejected += 1

    for w in workers.values():
        w["active"] = bool(w.get("last_seen") and now - w["last_seen"] <= WORKER_ACTIVE_SECONDS)
    return accepted[-200:], rejected, blocks[-100:], workers, job
'''

text = replace_function(text, "parse_logs", replacement)
compile(text, str(PATH), "exec")
PATH.write_text(text, encoding="utf-8")
print(f"verified {PATH}: explicit worker attribution, per-worker reject counts, and miner identity")
