#!/usr/bin/env python3
"""Apply deterministic Stratum job-refresh and stale-submit hardening."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text(encoding="utf-8")

old = 'same_value = int(job.get("value") or 0) == new_value'
new = 'same_value = int(job.get("value") or 0) == miner_value'
count = text.count(old)
if count != 1:
    raise RuntimeError(f"same-value marker mismatch: expected 1, found {count}")
text = text.replace(old, new, 1)

old = '''        if not job:\n            emit("WARN", f"REJECT reason=stale-job worker={self.worker} job={job_id} height={job.get('height')} ntime={ntime_hex} nonce={nonce_hex}")'''
new = '''        if not job:\n            emit("WARN", f"REJECT reason=stale-job worker={self.worker} job={job_id} height=? ntime={ntime_hex} nonce={nonce_hex}")'''
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

PATH.write_text(text, encoding="utf-8")
print("patched Stratum job refresh + stale submit handling")
