#!/usr/bin/env python3
"""Repair generated Stratum reject attribution after server.py generation."""
import re
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "stratum" / "server_full.py"
text = PATH.read_text(encoding="utf-8")

pattern = r'(REJECT reason=low-difficulty worker=)\? (job=\{job_id\})'
text, count = re.subn(pattern, r'\1{self.worker} \2', text, count=1)
if count != 1:
    raise RuntimeError(f"low-difficulty worker attribution marker mismatch: expected 1, found {count}")

if 'REJECT reason=low-difficulty worker={self.worker}' not in text:
    raise RuntimeError("worker attribution patch did not apply")

PATH.write_text(text, encoding="utf-8")
print("patched Stratum low-difficulty worker attribution")
