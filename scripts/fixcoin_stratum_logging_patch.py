#!/usr/bin/env python3
"""Ensure generated low-difficulty rejects retain the authenticated worker."""
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "stratum" / "server_full.py"
text = PATH.read_text(encoding="utf-8")
lines = text.splitlines(keepends=True)
changed = 0
for i, line in enumerate(lines):
    if "REJECT reason=low-difficulty" not in line:
        continue
    if "worker=?" in line:
        lines[i] = line.replace("worker=?", "worker={self.worker}", 1)
        changed += 1
        break
    if "worker={self.worker}" in line:
        changed = 1
        break

if changed != 1:
    raise RuntimeError("could not locate low-difficulty reject worker attribution")

text = "".join(lines)
if "REJECT reason=low-difficulty worker={self.worker}" not in text:
    raise RuntimeError("low-difficulty worker attribution is not present after patch")
PATH.write_text(text, encoding="utf-8")
print("patched Stratum low-difficulty worker attribution")
