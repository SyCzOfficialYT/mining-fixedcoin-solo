#!/usr/bin/env python3
"""Validate FixedCoin Stratum share-difficulty enforcement in the generated adapter."""
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "stratum" / "server_full.py"
text = PATH.read_text()

# Low-difficulty shares must remain Stratum rejections.  The consensus patch
# must never turn them into accepted/credited shares, and this guard is
# intentionally idempotent so the build pipeline cannot regress the policy.
required = (
    'REJECT reason=low-difficulty',
    'self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})',
)
for marker in required:
    if marker not in text:
        raise RuntimeError(f"generated Stratum low-difficulty rejection missing: {marker}")

if "ACCEPT low-difficulty share" in text:
    raise RuntimeError("generated Stratum low-difficulty acceptance path remains")

if text.count('error": [23, "low difficulty", None]') != 1:
    raise RuntimeError("low-difficulty rejection mismatch")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"verified {PATH}: FixedCoin low-difficulty shares remain rejected")
