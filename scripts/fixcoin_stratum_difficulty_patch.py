#!/usr/bin/env python3
"""Make solo Stratum share acceptance explicit and regression-safe.

FixedCoin solo mode accepts any cryptographically valid submitted share for
accounting/visibility, even when its proof-of-work is below the advertised
pool share target.  Network/block validity is still enforced by the block
candidate check and FixedCoin Core.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

# Replace the generated low-difficulty rejection/acceptance branch as one
# unit.  The branch must terminate after sending the Stratum response so it
# cannot fall through and send a second response or double-count the share.
pattern = re.compile(
    r"(?ms)^        if h_int > difficulty_to_target\(need\):\n"
    r".*?^        if share_work >= self\.diff:"
)

replacement = '''        if h_int > difficulty_to_target(need):
            credited = share_work
            self.shares_ok += 1
            _bump_worker(self.worker, True)
            _record_share(
                self.worker,
                share_work,
                credited,
                net_diff,
                hhex,
                job["height"],
                True,
            )
            _add_round_share(credited, share_work, net_diff, job["height"])
            self.send({"id": mid, "result": True, "error": None})
            _save_stats()
            emit(
                "OK",
                f"ACCEPT low-difficulty worker={self.worker} job={job_id} "
                f"height={job['height']} work={share_work:.6f} "
                f"required={need:.6f} hash={hhex[:24]}",
            )
            return
        if share_work >= self.diff:'''

matches = list(pattern.finditer(text))
if len(matches) != 1:
    raise RuntimeError(
        f"low-difficulty branch marker mismatch: expected 1, found {len(matches)}"
    )

text = text[:matches[0].start()] + replacement + text[matches[0].end():]

# The generated adapter must not contain the old Stratum rejection anymore.
if 'error": [23, "low difficulty", None]' in text:
    raise RuntimeError("low-difficulty rejection path remains")
if 'ACCEPT low-difficulty worker=' not in text:
    raise RuntimeError("explicit low-difficulty acceptance path missing")
if text.count('return\n        if share_work >= self.diff:') != 1:
    raise RuntimeError("low-difficulty branch does not terminate cleanly")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"patched {PATH}: solo low-difficulty shares are accepted once and credited by actual work")
