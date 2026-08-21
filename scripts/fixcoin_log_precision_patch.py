#!/usr/bin/env python3
"""Keep tiny share/network percentages visible in the generated Stratum logs."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"

text = PATH.read_text()
lines = text.splitlines(keepends=True)

# Patch the generated ACCEPT expression without using a brittle regex over
# nested f-string braces. The pinned adapter's source layout may change.
share_matches = [
    i for i, line in enumerate(lines)
    if 'ACCEPT #' in line and 'share_work' in line and 'pct' in line and ':.3f' in line
]
if len(share_matches) != 1:
    raise RuntimeError(f"ACCEPT log line mismatch: expected 1, found {len(share_matches)}")
lines[share_matches[0]] = lines[share_matches[0]].replace('{pct:.3f}', '{pct:.6f}', 1)

round_matches = [
    i for i, line in enumerate(lines)
    if 'round=' in line and 'effort' in line and ':.2f' in line
]
if len(round_matches) != 1:
    raise RuntimeError(f"round effort log line mismatch: expected 1, found {len(round_matches)}")
lines[round_matches[0]] = lines[round_matches[0]].replace('{effort:.2f}', '{effort:.4f}', 1)

PATH.write_text(''.join(lines))
print("patched log precision: share_pct=.6f, round_effort=.4f")
