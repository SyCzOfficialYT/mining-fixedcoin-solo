#!/usr/bin/env python3
"""Make dashboard worker attribution patch idempotent.

The dashboard is assembled by several ordered patch scripts. This patch must
be safe when an earlier patch has already changed the same parser.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "monitor" / "app.py"
text = PATH.read_text(encoding="utf-8")

optional_accept = 'ACCEPT(?:\\s+worker=(\\S+))?\\s+#(\\d+)\\s+work=([0-9.]+).*?(?:pool|pool_diff)=([0-9.]+).*?hash=([0-9a-fA-F]+)'
legacy_accept = 'ACCEPT\\s+#(\\d+)\\s+work=([0-9.]+).*?(?:pool|pool_diff)=([0-9.]+).*?hash=([0-9a-fA-F]+)'
if optional_accept not in text and legacy_accept in text:
    text = text.replace(legacy_accept, optional_accept, 1)

if 'worker_hint,num,work,diff,h=m.groups()' not in text:
    legacy_unpack = 'num,work,diff,h=m.groups(); worker=current_worker or "unknown"'
    if legacy_unpack in text:
        text = text.replace(legacy_unpack, 'worker_hint,num,work,diff,h=m.groups(); worker=worker_hint or current_worker or "unknown"', 1)

identity_marker = 'w["miner_family"],w["miner_variant"],w["miner_version"]'
if identity_marker not in text:
    legacy_auth = 'name,diff=m.groups(); current_worker=name\n            w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(diff)})\n            w["difficulty"]=float(diff); w["last_seen"]=ts'
    if legacy_auth in text:
        replacement = 'name,diff=m.groups(); current_worker=name\n            w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(diff)})\n            w["difficulty"]=float(diff); w["last_seen"]=ts\n            mi=re.search(r"miner=([^/\\s]+)/([^\\s]+)\\s+version=([^\\s]+)",line,re.I)\n            if mi:\n                w["miner_family"],w["miner_variant"],w["miner_version"]=mi.groups()\n            w["vardiff"]=bool(re.search(r"mode=vardiff=True",line,re.I))'
        text = text.replace(legacy_auth, replacement, 1)

required = (optional_accept, 'worker_hint,num,work,diff,h=m.groups()', identity_marker)
missing = [marker for marker in required if marker not in text]
if missing:
    raise RuntimeError("dashboard worker attribution markers missing: " + ", ".join(missing))

compile(text, str(PATH), "exec")
PATH.write_text(text, encoding="utf-8")
print(f"verified {PATH}: worker-safe ACCEPT parsing and miner identity")
