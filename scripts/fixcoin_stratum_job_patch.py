#!/usr/bin/env python3
"""Apply deterministic Stratum job-refresh and stale-submit hardening."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text(encoding="utf-8")

desired = '''            if (self.current_id and self.last_height == height and self.last_prevhash == prevhash
                    and self.current_id in self.jobs):
                job = self.jobs[self.current_id]
                same_txs = (len(other_tx) == len(job.get("other_tx") or [])
                            and all(a == b for a, b in zip(other_tx, job.get("other_tx") or [])))
                same_value = int(job.get("value") or 0) == miner_value
                if same_txs and same_value:
                    job["ntime"] = max(int(job.get("ntime") or 0), int(tmpl["curtime"]))
                    job["net_diff"] = net_diff
                    return job, False
'''
legacy = '''            if (self.current_id and self.last_height == height and self.last_prevhash == prevhash
                    and self.current_id in self.jobs):
                job = self.jobs[self.current_id]
                same_txs = (len(other_tx) == len(job.get("other_tx") or [])
                            and all(a == b for a, b in zip(other_tx, job.get("other_tx") or [])))
                same_value = int(job.get("value") or 0) == new_value
                if same_txs and same_value:
                    job["ntime"] = tmpl["curtime"]
                    job["template"] = tmpl
                    job["net_diff"] = net_diff
                    return job, False
'''
stable = '''            if (self.current_id and self.last_height == height and self.last_prevhash == prevhash
                    and self.current_id in self.jobs):
                job = self.jobs[self.current_id]
                # Same height is the same Stratum round. Refresh only mutable
                # time/network metadata; never replace the coinbase or job id.
                # Keep nTime monotonic so miners never receive a timestamp that
                # moves backwards after a node clock/template refresh.
                job["ntime"] = max(int(job.get("ntime") or 0), int(tmpl["curtime"]))
                job["net_diff"] = net_diff
                return job, False
'''
if desired not in text:
    if legacy in text:
        text = text.replace(legacy, desired, 1)
    elif stable in text:
        text = text.replace(stable, desired, 1)
    else:
        raise RuntimeError("same-height job refresh marker not found")

old = '''        if not job:
            emit("WARN", f"REJECT reason=stale-job worker={self.worker} job={job_id} height={job.get('height')} ntime={ntime_hex} nonce={nonce_hex}")'''
new = '''        if not job:
            emit("WARN", f"REJECT reason=stale-job worker={self.worker} job={job_id} height=? ntime={ntime_hex} nonce={nonce_hex}")'''
if old in text:
    text = text.replace(old, new, 1)
elif 'job={job_id} height=? ntime={ntime_hex} nonce={nonce_hex}' not in text:
    raise RuntimeError("stale-job marker not found")

if 'same_value = int(job.get("value") or 0) == miner_value' not in text:
    raise RuntimeError("miner payout comparison is missing")
if 'same_value = int(job.get("value") or 0) == new_value' in text:
    raise RuntimeError("gross GBT value is still compared with miner value")
if 'job={job_id} height=? ntime={ntime_hex} nonce={nonce_hex}' not in text:
    raise RuntimeError("safe stale-job logging missing")

PATH.write_text(text, encoding="utf-8")
print("patched Stratum job refresh + stale submit handling")
