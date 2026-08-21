#!/usr/bin/env python3
"""Keep tiny share/network percentages visible in the generated Stratum logs."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"

text = PATH.read_text()

# The pinned FreeCash adapter has changed the exact f-string variable names
# over time. Do not depend on a specific ``pct``/``effort`` name. Patch only
# the generated ACCEPT log line and only the format fields that are actually
# followed by percentage markers.
lines = text.splitlines(keepends=True)
accept_indexes = [
    i for i, line in enumerate(lines)
    if "ACCEPT" in line and "pool=" in line and "round=" in line
]

if len(accept_indexes) != 1:
    raise RuntimeError(
        f"ACCEPT log line mismatch: expected 1, found {len(accept_indexes)}"
    )

idx = accept_indexes[0]
line = lines[idx]

# Share percentage: the field is inside parentheses, e.g. ({pct:.3f}%).
share_re = re.compile(
    r"(\([^\n]*?\{[^}\n]*:\s*)\.\d+f(?=\s*\}\s*%\))"
)
line, share_count = share_re.subn(r"\1.6f", line, count=1)

# Round effort: e.g. round={effort:.2f}%.
round_re = re.compile(
    r"(round=[^\n]*?\{[^}\n]*:\s*)\.\d+f(?=\s*\}\s*%)"
)
line, round_count = round_re.subn(r"\1.4f", line, count=1)

if share_count != 1:
    raise RuntimeError(
        f"share percentage formatting marker mismatch: expected 1, found {share_count}"
    )
if round_count != 1:
    raise RuntimeError(
        f"round effort formatting marker mismatch: expected 1, found {round_count}"
    )

lines[idx] = line
PATH.write_text("".join(lines))
print(f"patched log precision: share_pct={share_count}, round_effort={round_count}")
