#!/usr/bin/env python3
"""Enforce the configured FixedCoin Stratum share difficulty.

The consensus patch historically accepted cryptographically valid hashes below
our advertised pool difficulty. That is useful for generic solo accounting,
but it is wrong for a fixed-difficulty Stratum endpoint: the miner must only
receive an accepted share when the submitted PoW meets the advertised target.

Network/block validation remains handled by FixedCoin Core.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

old = '''            need = self.effective_min_diff()\n            if h_int > difficulty_to_target(need):\n                emit("WARN", f"REJECT reason=low-difficulty worker={self.worker} job={job_id} height={job['height']} share_diff={share_work:.6f} required_diff={need:.6f} fixed_diff={self.diff:.6f} ntime={ntime_hex} nonce={nonce_hex} hash={hhex[:24]}")\n                emit("INFO", f"ACCEPT low-difficulty share worker={self.worker} job={job_id} height={job['height']} share_diff={share_work:.6f} advertised_diff={need:.6f} fixed_diff={self.diff:.6f} ntime={ntime_hex} nonce={nonce_hex} hash={hhex[:24]}")\n                _bump_worker(self.worker, ok=True)\n                _record_share(self.worker, share_work, self.diff, job.get("network_diff", 0.0), hhex, job["height"], accepted=True)\n                _add_round_share(self.diff, share_work, job.get("network_diff", 0.0), job["height"])\n                self.send({"id": mid, "result": True, "error": None})\n                self.shares_bad += 1; _bump_worker(self.worker, False); _save_stats()\n                return\n'''

new = '''            need = self.effective_min_diff()\n            share_target = difficulty_to_target(need)\n            if h_int > share_target:\n                emit(\n                    "WARN",\n                    f"REJECT reason=low-difficulty worker={self.worker} job={job_id} "\n                    f"height={job['height']} share_diff={share_work:.6f} "\n                    f"required_diff={need:.6f} fixed_diff={self.diff:.6f} "\n                    f"ntime={ntime_hex} nonce={nonce_hex} hash={hhex[:64]}"\n                )\n                self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})\n                self.shares_bad += 1\n                _bump_worker(self.worker, False)\n                _save_stats()\n                return\n'''

count = text.count(old)
if count != 1:
    raise RuntimeError(f"low-difficulty block mismatch: expected 1, found {count}")

text = text.replace(old, new, 1)

# Regression guards: the generated adapter must reject below-target shares and
# must no longer contain the old accounting/acceptance path.
if 'share_target = difficulty_to_target(need)' not in text:
    raise RuntimeError("share target guard missing")
if 'error": [23, "low difficulty", None]' not in text:
    raise RuntimeError("low-difficulty rejection missing")
if 'ACCEPT low-difficulty share' in text:
    raise RuntimeError("old low-difficulty acceptance path remains")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"patched {PATH}: fixed Stratum difficulty enforcement")
