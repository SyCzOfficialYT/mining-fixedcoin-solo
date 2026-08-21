#!/usr/bin/env python3
"""Keep tiny share/network percentages visible in the generated Stratum logs."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"

text = PATH.read_text()

# The pinned FreeCash adapter has changed the exact f-string variable names
# over time. Do not depend on a specific ``pct``/``effort`` expression.
# Instead, patch only the generated ACCEPT log line, where the share and
# round percentages are presentation-only values.
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

# Preserve every calculation and value; only increase display precision.
share_line, share_count = re.subn(r"\.3f(?=\s*%?\)?|\s*%)", ".6f", line, count=1)
round_line, round_count = re.subn(r"\.2f(?=\s*%)", ".4f", share_line, count=1)

# Some generated revisions use a different precision already. In that case,
# target the percentage fields by their surrounding text instead of silently
# doing nothing.
if share_count == 0:
    round_match = re.search(r"(\([^\n%]*?)\.(\d+)f(\s*%\))", round_line)
    if round_match:
        round_line = round_line[:round_match.start(2)] + "6" + round_line[round_match.end(2):]
        share_count = 1

if round_count == 0:
    effort_match = re.search(r"(round=.*?\.)\d+f(\s*%)", round_line)
    if effort_match:
        round_line = round_line[:effort_match.start()] + effort_match.group(1) + "4f" + round_line[effort_match.end():]
        round_count = 1

if share_count != 1:
    raise RuntimeError(
        f"share percentage formatting marker mismatch: expected 1, found {share_count}"
    )
if round_count != 1:
    raise RuntimeError(
        f"round effort formatting marker mismatch: expected 1, found {round_count}"
    )

lines[idx] = round_line
PATH.write_text("".join(lines))
print(f"patched log precision: share_pct={share_count}, round_effort={round_count}")
