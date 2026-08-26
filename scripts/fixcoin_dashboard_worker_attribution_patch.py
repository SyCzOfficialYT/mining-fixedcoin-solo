#!/usr/bin/env python3
"""Make dashboard log parsing worker-safe and preserve miner identity."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "monitor" / "app.py"
text = PATH.read_text(encoding="utf-8")

old_accept = 'm=re.search(r"ACCEPT\\s+#(\\d+)\\s+work=([0-9.]+).*?(?:pool|pool_diff)=([0-9.]+).*?hash=([0-9a-fA-F]+)",line,re.I)'
new_accept = 'm=re.search(r"ACCEPT(?:\\s+worker=(\\S+))?\\s+#(\\d+)\\s+work=([0-9.]+).*?(?:pool|pool_diff)=([0-9.]+).*?hash=([0-9a-fA-F]+)",line,re.I)'
if old_accept in text:
    text = text.replace(old_accept, new_accept, 1)

old_unpack = 'num,work,diff,h=m.groups(); worker=current_worker or "unknown"'
new_unpack = 'worker_hint,num,work,diff,h=m.groups(); worker=worker_hint or current_worker or "unknown"'
if old_unpack in text:
    text = text.replace(old_unpack, new_unpack, 1)

old_auth = 'name,diff=m.groups(); current_worker=name\n            w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(diff)})\n            w["difficulty"]=float(diff); w["last_seen"]=ts'
new_auth = '''name,diff=m.groups(); current_worker=name
            w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(diff)})
            w["difficulty"]=float(diff); w["last_seen"]=ts
            mi=re.search(r"miner=([^/\\s]+)/([^\\s]+)\\s+version=([^\\s]+)",line,re.I)
            if mi:
                w["miner_family"],w["miner_variant"],w["miner_version"]=mi.groups()
            w["vardiff"]=bool(re.search(r"mode=vardiff=True",line,re.I))'''
if old_auth in text:
    text = text.replace(old_auth, new_auth, 1)

required = (
    'ACCEPT(?:\\s+worker=(\\S+))?',
    'worker_hint,num,work,diff,h=m.groups()',
    'miner_family",w["miner_variant"],w["miner_version"]',
)
for marker in required:
    if marker not in text:
        raise RuntimeError(f"dashboard worker attribution marker missing: {marker}")

compile(text, str(PATH), "exec")
PATH.write_text(text, encoding="utf-8")
print(f"verified {PATH}: accepted shares and miner identity are attributed per worker")
