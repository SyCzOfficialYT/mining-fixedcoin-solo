#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
P=ROOT/'monitor/app.py'
s=P.read_text()
old='''            name,diff=m.groups(); current_worker=name\n            w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(diff)})\n            w["difficulty"]=float(diff); w["last_seen"]=ts\n'''
new='''            name,diff=m.groups(); current_worker=name\n            w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(diff)})\n            w["difficulty"]=float(diff); w["last_seen"]=ts\n            mode_m=re.search(r"\\bmode=(\\S+)",line,re.I)\n            miner_m=re.search(r"\\bminer=([^\\s]+)",line,re.I)\n            version_m=re.search(r"\\bversion=([^\\s]+)",line,re.I)\n            if mode_m: w["vardiff"]=mode_m.group(1).lower() in ("vardiff=true","true","on")\n            if miner_m:\n                ident=miner_m.group(1); parts=ident.split("/",1); w["miner_family"]=parts[0]; w["miner_variant"]=parts[1] if len(parts)>1 else ""\n            if version_m: w["miner_version"]=version_m.group(1)\n'''
if old not in s: raise SystemExit('authorize parser marker not found')
s=s.replace(old,new,1)
P.write_text(s)
print('patched dashboard worker parser: miner identity + vardiff')
