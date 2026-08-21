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
if share_count != 1:
    raise RuntimeError(f"share percentage formatting marker mismatch: expected 1, found {share_count}")
if round_count != 1:
    raise RuntimeError(f"round effort formatting marker mismatch: expected 1, found {round_count}")

PATH.write_text(text.replace(share_old, share_new, 1).replace(round_old, round_new, 1))
print(f"patched log precision: share_pct={share_count}, round_effort={round_count}")
