#!/usr/bin/env python3
"""Keep tiny share/network percentages visible in the generated Stratum logs."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"

text = PATH.read_text()

# Patch the exact ACCEPT formatting expression used by the pinned adapter.
# The generated line is split across two adjacent source lines, so match the
# complete f-string fragment rather than requiring an entire source line.
share_re = re.compile(r"(f\"ACCEPT #\{self\.shares_ok\} work=\{share_work:\.0f\} \(\{pct:)\.3f(\}%\) ")
text, share_count = share_re.subn(r"\g<1>.6f\2", text, count=1)

round_re = re.compile(r"(round=\{effort:)\.2f(% hash=\{hhex\[:16\]\}\")")
text, round_count = round_re.subn(r"\g<1>.4f\2", text, count=1)

if share_count != 1:
    raise RuntimeError(
        f"share percentage formatting marker mismatch: expected 1, found {share_count}"
    )
if round_count != 1:
    raise RuntimeError(
        f"round effort formatting marker mismatch: expected 1, found {round_count}"
    )

PATH.write_text(text)
print(f"patched log precision: share_pct={share_count}, round_effort={round_count}")
