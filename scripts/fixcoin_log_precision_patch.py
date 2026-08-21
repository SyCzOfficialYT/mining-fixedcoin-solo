#!/usr/bin/env python3
"""Keep tiny share/network percentages visible in the generated Stratum logs."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"

text = PATH.read_text()

# The generated FreeCash adapter formats these values inside f-string fields:
#   ({pct:.3f}%)
#   round={effort:.2f}%
# The previous patch looked for ``pct: .3f`` outside the braces and therefore
# never matched the generated source. Only presentation precision is changed;
# the underlying share/network values remain untouched.
share_re = re.compile(r"(\{\s*pct\s*:\s*)\.3f(?=\s*\})")
text, share_count = share_re.subn(r"\1.6f", text, count=1)

round_re = re.compile(r"(\{\s*effort\s*:\s*)\.2f(?=\s*\})")
text, round_count = round_re.subn(r"\1.4f", text, count=1)

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
