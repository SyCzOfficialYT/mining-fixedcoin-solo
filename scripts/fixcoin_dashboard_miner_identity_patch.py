#!/usr/bin/env python3
"""Extend dashboard worker parsing with miner identity and VarDiff state.

The parser in monitor/app.py already extracts authorize lines with a regex and
stores the worker in ``workers``.  Keep this patch anchored to that real block
instead of depending on an older multiline formatting variant.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "monitor" / "app.py"
s = APP.read_text()

old = '''        if m:\n            name,diff=m.groups(); current_worker=name\n            w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(diff)})\n            w["difficulty"]=float(diff); w["last_seen"]=ts\n'''

new = '''        if m:\n            name,diff=m.groups(); current_worker=name\n            w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(diff)})\n            w["difficulty"]=float(diff); w["last_seen"]=ts\n            mode_m=re.search(r"\\bmode=(\\S+)",line,re.I)\n            miner_m=re.search(r"\\bminer=([^\\s]+)",line,re.I)\n            version_m=re.search(r"\\bversion=([^\\s]+)",line,re.I)\n            user_agent_m=re.search(r"\\b(?:ua|user_agent)=([^\\s]+)",line,re.I)\n            if mode_m:\n                mode=mode_m.group(1).lower()\n                w["vardiff"]=mode in ("vardiff=true","true","on")\n            if miner_m:\n                ident=miner_m.group(1)\n                parts=ident.split("/",1)\n                w["miner_family"]=parts[0]\n                w["miner_variant"]=parts[1] if len(parts)>1 else ""\n            if version_m:\n                w["miner_version"]=version_m.group(1)\n            if user_agent_m:\n                w["user_agent"]=user_agent_m.group(1)\n'''

if old not in s:
    raise RuntimeError("authorize parser block not found in monitor/app.py")

s = s.replace(old, new, 1)
compile(s, str(APP), "exec")
APP.write_text(s)
print("patched dashboard worker parser: miner identity + vardiff + user-agent")
