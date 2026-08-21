#!/usr/bin/env python3
"""Enforce the configured FixedCoin Stratum share difficulty."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

# fixcoin_consensus_patch.py runs immediately before this script and changes
# the low-difficulty branch into an accounting accept. Match that post-patch
# form and turn it into a real Stratum rejection.
pattern = re.compile(
    r'''(?ms)^            need = self\.effective_min_diff\(\)\n.*?^            self\.send\(\{"id": mid, "result": True, "error": None\}\)'''
)

replacement = '''            need = self.effective_min_diff()
            share_target = difficulty_to_target(need)
            if h_int > share_target:
                emit(
                    "WARN",
                    f"REJECT reason=low-difficulty worker={self.worker} job={job_id} "
                    f"height={job['height']} share_diff={share_work:.6f} "
                    f"required_diff={need:.6f} fixed_diff={self.diff:.6f} "
                    f"ntime={ntime_hex} nonce={nonce_hex} hash={hhex[:64]}"
                )
                self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})
                self.shares_bad += 1
                _bump_worker(self.worker, False)
                _save_stats()
                return'''

matches = pattern.findall(text)
if len(matches) != 1:
    raise RuntimeError(
        f"low-difficulty post-consensus block mismatch: expected 1, found {len(matches)}"
    )

text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise RuntimeError(f"low-difficulty replacement failed: {count}")

if text.count('share_target = difficulty_to_target(need)') != 1:
    raise RuntimeError("share target guard mismatch")
if text.count('error": [23, "low difficulty", None]') != 1:
    raise RuntimeError("low-difficulty rejection mismatch")
if 'ACCEPT low-difficulty share' in text:
    raise RuntimeError("old low-difficulty acceptance path remains")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"patched {PATH}: fixed Stratum difficulty enforcement")
