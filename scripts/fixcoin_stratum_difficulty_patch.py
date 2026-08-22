#!/usr/bin/env python3
"""Validate strict FixedCoin Stratum share-difficulty enforcement."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

# Normal Stratum shares below the advertised fixed pool difficulty must remain
# rejected. A genuine network-valid block candidate is checked separately by
# the block-target path and must never be accepted through this share path.
required_rejection = 'self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})'
if text.count(required_rejection) != 1:
    raise RuntimeError(
        f"generated Stratum low-difficulty rejection mismatch: expected 1, found {text.count(required_rejection)}"
    )

if "ACCEPT low-difficulty" in text:
    raise RuntimeError("generated Stratum low-difficulty acceptance bypass remains")

if 'result": True, "error": None' in text and "low-difficulty" in text:
    raise RuntimeError("generated Stratum contains a low-difficulty success response")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"verified {PATH}: FixedCoin low-difficulty shares remain rejected")
