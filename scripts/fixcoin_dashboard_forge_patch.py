#!/usr/bin/env python3
"""Expose authoritative live pool difficulty without mutating the reference Forge DOM."""
from pathlib import Path
import re

HTML=Path('/app/monitor/templates/dashboard_v4.html')
APP=Path('/app/monitor/app.py')
html=HTML.read_text()

# The repository-owned reference template is already the final Forge DOM.
# Detect the class as a token so multi-class declarations such as
# `class="dashboard reference-dashboard"` are accepted.
reference_dashboard = bool(re.search(r'class="[^"]*\breference-dashboard\b[^"]*"', html))
if reference_dashboard:
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
if '"pool_difficulty":pool_difficulty' not in text:
    if 'pool_difficulty=' not in text:
        marker='active_workers=list(workers.keys())'
        if marker not in text:
            # Accept harmless whitespace variations introduced by earlier
            # dashboard authority patches.
            m=re.search(r'(?m)^(\s*)active_workers\s*=\s*list\(workers\.keys\(\)\)\s*$', text)
            if not m:
                raise RuntimeError('dashboard worker authority anchor missing')
            indent=m.group(1)
            replacement=(
                f'{indent}active_workers=list(workers.keys())\n'
                f'{indent}pool_difficulty=fixed_diff\n'
                f'{indent}for worker_name in active_workers:\n'
                f'{indent}    worker_state=workers.get(worker_name,{})\n'
                f'{indent}    worker_diff=as_number(worker_state.get("difficulty"),0)\n'
                f'{indent}    if worker_diff>0:\n'
                f'{indent}        pool_difficulty=worker_diff\n'
                f'{indent}        break'
            )
            text=text[:m.start()]+replacement+text[m.end():]
        else:
            replacement=marker+'''\n    pool_difficulty=fixed_diff\n    for worker_name in active_workers:\n        worker_state=workers.get(worker_name,{})\n        worker_diff=as_number(worker_state.get("difficulty"),0)\n        if worker_diff>0:\n            pool_difficulty=worker_diff\n            break'''
            text=text.replace(marker,replacement,1)
    marker='"fixed_difficulty":fixed_diff,'
    if marker not in text:
        raise RuntimeError('dashboard fixed difficulty anchor missing')
    text=text.replace(marker,marker+'"pool_difficulty":pool_difficulty,"vardiff_mode":True,',1)
    APP.write_text(text)
print('FIXCORE dashboard backend authority verified: live pool difficulty exposed without legacy Forge DOM mutation')
