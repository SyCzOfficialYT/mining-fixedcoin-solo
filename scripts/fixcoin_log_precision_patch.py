#!/usr/bin/env python3
"""Keep tiny share/network percentages visible in the generated Stratum logs."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"

text = PATH.read_text()

# The generated FreeCash adapter calls the share percentage `pct` and the
# STATS round percentage `effort`.  The previous patch incorrectly searched
# for a `share_work` formatted field, which does not exist in the pinned base.
# Only change presentation precision; never change the underlying values.
share_re = re.compile(r"(pct\s*:\s*)\.3f")
text, share_count = share_re.subn(r"\1.6f", text, count=1)

round_re = re.compile(r"(effort\s*:\s*)\.2f")
text, round_count = round_re.subn(r"\1.4f", text, count=1)

if share_count != 1:
    raise RuntimeError(f"share percentage formatting marker mismatch: expected 1, found {share_count}")
if round_count != 1:
    raise RuntimeError(f"round effort formatting marker mismatch: expected 1, found {round_count}")

PATH.write_text(text)
print(f"patched log precision: share_pct={share_count}, round_effort={round_count}")
