#!/usr/bin/env python3
"""Enforce configured FixedCoin Stratum share difficulty."""
from pathlib import Path
import re

PATH = Path(__file__).resolve().parent.parent / "stratum" / "server_full.py"
text = PATH.read_text()

# consensus patch inserts a single low-difficulty acceptance block. Replace
# only that block; never rewrite the surrounding control-flow structure.
pattern = re.compile(
    r'(?m)^(?P<i>[ \t]*)emit\("INFO", f"ACCEPT low-difficulty share worker=.*\n'
    r'(?P=i)_bump_worker\(self\.worker, ok=True\)\n'
    r'(?P=i)_record_share\(self\.worker, share_work, self\.diff, job\.get\("network_diff", 0\.0\), hhex, job\["height"\], accepted=True\)\n'
    r'(?P=i)_add_round_share\(self\.diff, share_work, job\.get\("network_diff", 0\.0\), job\["height"\]\)\n'
    r'(?P=i)self\.send\(\{"id": mid, "result": True, "error": None\}\)'
)
match = pattern.search(text)
if not match:
    raise RuntimeError("generated low-difficulty acceptance block not found")

i = match.group("i")
replacement = (
    i + 'emit("WARN", f"REJECT reason=low-difficulty worker={self.worker} job={job_id} "\n'
    + i + '     f"height={job[\'height\']} share_diff={share_work:.6f} required_diff={need:.6f} "\n'
    + i + '     f"fixed_diff={self.diff:.6f} ntime={ntime_hex} nonce={nonce_hex} hash={hhex[:64]}")\n'
    + i + 'self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})\n'
    + i + 'self.shares_bad += 1\n'
    + i + '_bump_worker(self.worker, False)\n'
    + i + '_save_stats()\n'
    + i + 'return'
)
text = text[:match.start()] + replacement + text[match.end():]

if "ACCEPT low-difficulty share" in text:
    raise RuntimeError("old low-difficulty acceptance path remains")
if text.count('error": [23, "low difficulty", None]') != 1:
    raise RuntimeError("low-difficulty rejection mismatch")
compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"patched {PATH}: fixed Stratum difficulty enforcement")
