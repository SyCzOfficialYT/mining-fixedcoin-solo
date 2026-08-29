#!/usr/bin/env python3
"""Apply FixedCoin Stratum job-refresh and stale-submit handling fixes.

The generated Stratum adapter polls GBT periodically. A refresh for the same
network tip must keep the existing job instead of creating a new job on every
poll. The submit path must handle unknown/stale job IDs without dereferencing
None.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

# GBT coinbasevalue is the complete subsidy+fee value. The generated adapter's
# job value is the actual miner payout after any accounting transformation.
# Comparing the two makes every unchanged GBT refresh look like a new job.
old = 'same_value = int(job.get("value") or 0) == new_value'
new = 'same_value = int(job.get("value") or 0) == miner_value'
count = text.count(old)
if count != 1:
    raise RuntimeError(f"same-value marker mismatch: expected 1, found {count}")
text = text.replace(old, new, 1)

# An unknown job ID is a normal stale-share condition. Never call job.get()
# before checking whether the job exists.
old = '''        if not job:
            emit("WARN", f"REJECT reason=stale-job worker={self.worker} job={job_id} height={job.get('height')} ntime={ntime_hex} nonce={nonce_hex}")'''
new = '''        if not job:
            emit("WARN", f"REJECT reason=stale-job worker={self.worker} job={job_id} height=? ntime={ntime_hex} nonce={nonce_hex}")'''
count = text.count(old)
if count != 1:
    raise RuntimeError(f"stale-job marker mismatch: expected 1, found {count}")
text = text.replace(old, new, 1)

if 'same_value = int(job.get("value") or 0) == miner_value' not in text:
    raise RuntimeError("miner-value refresh guard missing")
if 'same_value = int(job.get("value") or 0) == new_value' in text:
    raise RuntimeError("gross GBT value is still compared with miner value")
if 'job={job_id} height=? ntime={ntime_hex} nonce={nonce_hex}' not in text:
    raise RuntimeError("safe stale-job logging missing")

PATH.write_text(text)
print("patched Stratum job refresh + stale submit handling")
