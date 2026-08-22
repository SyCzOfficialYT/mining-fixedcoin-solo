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

# Do not search the entire generated adapter for a generic success response:
# mining.extranonce.subscribe and the normal accepted-share path legitimately
# return result=True. Validate only the actual low-difficulty branch.
low_diff_marker = "if h_int > difficulty_to_target(need):"
accepted_share_marker = "if share_work >= self.diff:"
if low_diff_marker not in text or accepted_share_marker not in text:
    raise RuntimeError("generated Stratum low-difficulty branch markers are missing")
low_diff_branch = text.split(low_diff_marker, 1)[1].split(accepted_share_marker, 1)[0]
if 'result": True, "error": None' in low_diff_branch:
    raise RuntimeError("generated Stratum low-difficulty branch contains a success response")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"verified {PATH}: FixedCoin low-difficulty shares remain rejected")
