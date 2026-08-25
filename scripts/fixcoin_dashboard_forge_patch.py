#!/usr/bin/env python3
"""Keep authoritative pool-difficulty telemetry without reapplying legacy Forge DOM patches."""
from pathlib import Path
import re

HTML=Path('/app/monitor/templates/dashboard_v4.html')
APP=Path('/app/monitor/app.py')
html=HTML.read_text()

# The repository-owned reference template is already the final Forge DOM. The
# historical Forge patch injected old HUD/forge.js contracts and is therefore
# deliberately skipped when the final template is present.
if 'class="reference-dashboard"' in html:
    print('dashboard Forge DOM already final; skipping legacy Forge HTML patch')
else:
    if 'id="forgeCore"' not in html:
        raise RuntimeError('FIXCORE mount missing')
    css_link='<link rel="stylesheet" href="/static/dashboard_v4_forge_hud.css?v=20260823-3">'
    if 'dashboard_v4_forge_hud.css' not in html:
        m=re.search(r'(<link rel="stylesheet" href="/static/dashboard_v4_forge(?:_motion)?\.css\?v=[^"]+">)',html)
        if m: html=html[:m.end()]+css_link+html[m.end():]
    HTML.write_text(html)

text=APP.read_text()
if 'pool_difficulty=' not in text:
    marker='    active_workers=list(workers.keys())\n'
    insert='''    active_workers=list(workers.keys())\n    pool_difficulty=fixed_diff\n    for worker_name in active_workers:\n        worker_state=workers.get(worker_name,{})\n        worker_diff=as_number(worker_state.get("difficulty"),0)\n        if worker_diff>0:\n            pool_difficulty=worker_diff\n            break\n'''
    if marker not in text: raise RuntimeError('dashboard worker authority anchor missing')
    text=text.replace(marker,insert,1)
if '"pool_difficulty":pool_difficulty' not in text:
    marker='"fixed_difficulty":fixed_diff,'
    if marker not in text: raise RuntimeError('dashboard fixed difficulty anchor missing')
    text=text.replace(marker,marker+'"pool_difficulty":pool_difficulty,"vardiff_mode":True,',1)
APP.write_text(text)
print('FIXCORE dashboard backend authority verified: live pool difficulty exposed without legacy Forge DOM mutation')
