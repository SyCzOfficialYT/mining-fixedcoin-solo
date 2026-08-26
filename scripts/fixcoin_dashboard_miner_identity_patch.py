#!/usr/bin/env python3
"""Extend dashboard worker parsing with miner identity and VarDiff state.

The dashboard parser has changed several times as the authoritative worker
telemetry was repaired. Keep this patch anchored to the actual difficulty
assignment instead of an exact multiline formatting variant.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "monitor" / "app.py"
s = APP.read_text()

# The authorize parser always records the canonical worker difficulty and
# last-seen timestamp. Anchor there so formatting/previous patches can evolve
# without making this patch fail the whole Docker build.
anchor = '            w["difficulty"]=float(diff); w["last_seen"]=ts\n'

addition = '''            mode_m=re.search(r"\\bmode=(\\S+)",line,re.I)\n            miner_m=re.search(r"\\bminer=([^\\s]+)",line,re.I)\n            version_m=re.search(r"\\bversion=([^\\s]+)",line,re.I)\n            user_agent_m=re.search(r"\\b(?:ua|user_agent)=([^\\s]+)",line,re.I)\n            if mode_m:\n                mode=mode_m.group(1).lower()\n                w["vardiff"]=mode in ("vardiff=true","true","on")\n            if miner_m:\n                ident=miner_m.group(1)\n                parts=ident.split("/",1)\n                w["miner_family"]=parts[0]\n                w["miner_variant"]=parts[1] if len(parts)>1 else ""\n            if version_m:\n                w["miner_version"]=version_m.group(1)\n            if user_agent_m:\n                w["user_agent"]=user_agent_m.group(1)\n'''

if 'w["miner_family"]' not in s:
    if anchor not in s:
        # Be tolerant of whitespace changes around the same semantic line.
        m = re.search(r'(?m)^\\s*w\["difficulty"\]=float\(diff\);\\s*w\["last_seen"\]=ts\\s*$', s)
        if not m:
            raise RuntimeError("authorize worker difficulty anchor not found in monitor/app.py")
        end = m.end()
        s = s[:end] + "\n" + addition.rstrip("\n") + s[end:]
    else:
        s = s.replace(anchor, anchor + addition, 1)

compile(s, str(APP), "exec")
APP.write_text(s)
print("patched dashboard worker parser: miner identity + vardiff + user-agent")
