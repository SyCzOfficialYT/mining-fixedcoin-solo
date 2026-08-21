#!/usr/bin/env python3
"""Keep tiny share/network percentages visible in the generated Stratum logs."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"

text = PATH.read_text()

# Share effort can legitimately be far below 0.001% at FixedCoin network
# difficulty. The old 3-decimal formatting rounded those values to 0.000%.
share_re = re.compile(r"(\{[^{}\n]*share_work[^{}\n]*):\.3f(\})")
text, share_count = share_re.subn(r"\1:.6f\2", text)

# Round effort is also useful below 0.01%, so keep four decimals in the
# human-readable STATS line. Do not touch the stored numeric value.
round_re = re.compile(r"(\{[^{}\n]*round_effort_pct[^{}\n]*):\.2f(\})")
text, round_count = round_re.subn(r"\1:.4f\2", text)

if share_count == 0:
    raise RuntimeError("share percentage formatting marker not found")
if round_count == 0:
    raise RuntimeError("round effort formatting marker not found")

PATH.write_text(text)
print(f"patched log precision: share_pct={share_count}, round_effort={round_count}")
