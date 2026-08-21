#!/usr/bin/env python3
"""Keep tiny share/network percentages visible in the generated Stratum logs."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"

text = PATH.read_text()

share_old = "{pct:.3f}%"
share_new = "{pct:.6f}%"
round_old = "round={effort:.2f}%"
round_new = "round={effort:.4f}%"

share_count = text.count(share_old)
round_count = text.count(round_old)

# The generated adapter can contain multiple round-effort log paths.
# Patch every occurrence instead of assuming exactly one.
if share_count < 1:
    raise RuntimeError(f"share percentage formatting marker not found: {share_old!r}")
if round_count < 1:
    raise RuntimeError(f"round effort formatting marker not found: {round_old!r}")

text = text.replace(share_old, share_new)
text = text.replace(round_old, round_new)
PATH.write_text(text)

print(f"patched log precision: share_pct={share_count}, round_effort={round_count}")
