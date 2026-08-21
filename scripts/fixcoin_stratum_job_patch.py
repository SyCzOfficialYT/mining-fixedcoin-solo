#!/usr/bin/env python3
"""Apply the FixedCoin Stratum job-refresh and submit-path fixes.

The generated Stratum adapter refreshes GBT periodically. A refresh for the
same network tip must keep the existing job instead of creating a new job on
every poll. The submit path must also handle unknown/stale job IDs without
trying to dereference a missing job.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

# `job["value"]` is the miner payout after the governance/dev deduction,
# whereas GBT `coinbasevalue` is the complete subsidy+fees. Comparing those
# values makes every 30s GBT refresh look like a new template. Compare the
# miner value to the miner value instead.
old = 'same_value = int(job.get("value") or 0) == new_value'
new = 'same_value = int(job.get("value") or 0) == miner_value'
count = text.count(old)
if count != 1:
    raise RuntimeError(f"same-value marker mismatch: expected 1, found {count}")
text = text.replace(old, new, 1)

# A stale job is a normal Stratum condition. Do not call job.get() before
# checking whether the job exists; that turns a clean stale-share rejection
# into an exception and can kill the client thread.
old = '''        if not job:\n            emit("WARN", f"REJECT reason=stale-job worker={self.worker} job={job_id} height={job.get('height')} ntime={ntime_hex} nonce={nonce_hex}")'''
new = '''        if not job:\n            emit("WARN", f"REJECT reason=stale-job worker={self.worker} job={job_id} height=? ntime={ntime_hex} nonce={nonce_hex}")'''
count = text.count(old)
if count != 1:
    raise RuntimeError(f"stale-job marker mismatch: expected 1, found {count}")
text = text.replace(old, new, 1)

# Regression guards: these are the two invariants this patch exists to keep.
if 'same_value = int(job.get("value") or 0) == miner_value' not in text:
    raise RuntimeError("miner-value refresh guard missing")
if 'job={job_id} height=? ntime={ntime_hex} nonce={nonce_hex}' not in text:
    raise RuntimeError("safe stale-job logging missing")
if 'same_value = int(job.get("value") or 0) == new_value' in text:
    raise RuntimeError("gross GBT value is still compared with miner value")

PATH.write_text(text)
print("patched Stratum job refresh + stale submit handling")
