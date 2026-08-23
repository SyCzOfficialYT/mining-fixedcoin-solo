#!/usr/bin/env python3
"""Make FIXCORE the only forge visualization and wire the live share HUD."""
from pathlib import Path
import re

HTML=Path('/app/monitor/templates/dashboard_v4.html')
APP=Path('/app/monitor/app.py')
html=HTML.read_text()

# Remove any legacy humanoid/raster miner mount left by older patches.
html=re.sub(r'\s*<div class="miner-reference-wrap"[^>]*>.*?</div>', '', html, count=1, flags=re.S)
html=re.sub(r'\s*<script[^>]+dashboard_v4_miner\.js[^>]*></script>', '', html, count=1)
html=re.sub(r'\s*<div class="anvil"[^>]*>.*?</div>\s*<div class="impact"[^>]*>.*?</div>', '', html, count=1, flags=re.S)
if 'id="forgeCore"' not in html:
    raise RuntimeError('FIXCORE mount missing after legacy miner cleanup')
if 'dashboard_v4_miner.js' in html or 'miner-reference' in html or '<img' in html or '<image' in html:
    raise RuntimeError('legacy miner markup survived FIXCORE dashboard patch')

# Live VarDiff HUD stylesheet: inject it exactly once regardless of the current
# dashboard forge stylesheet version.
css_link='<link rel="stylesheet" href="/static/dashboard_v4_forge_hud.css?v=20260823-3">'
html=re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_forge_hud\.css\?v=[^"]+">', '', html)
anchor='<link rel="stylesheet" href="/static/dashboard_v4_forge.css?v=20260823-5">'
if anchor in html:
    html=html.replace(anchor,anchor+css_link,1)
elif 'dashboard_v4_forge_hud.css' not in html:
    # Fall back to the first forge stylesheet if the forge version was bumped.
    m=re.search(r'(<link rel="stylesheet" href="/static/dashboard_v4_forge(?:_motion)?\.css\?v=[^"]+">)',html)
    if not m:
        raise RuntimeError('dashboard v4 forge stylesheet anchor missing')
    html=html[:m.end()]+css_link+html[m.end():]

hud='<div class="forge-vardiff-hud" id="forgeVarDiff"><span>VARDIFF MODE</span><strong id="poolDiffValue">—</strong><small id="poolDiffLabel">POOL DIFF · LIVE</small></div>'
if 'id="poolDiffValue"' not in html:
    anchor='<div class="forge-vignette"></div>'
    if anchor not in html:
        raise RuntimeError('forge vignette anchor missing')
    html=html.replace(anchor,anchor+hud,1)

# Load the HUD client exactly once. Do not depend on an old forge.js version.
html=re.sub(r'<script[^>]+dashboard_v4_forge_hud\.js\?v=[^>]+></script>', '', html)
script='<script defer src="/static/dashboard_v4_forge_hud.js?v=20260823-2"></script>'
forge_script=re.search(r'<script[^>]+dashboard_v4_forge\.js\?v=[^>]+></script>',html)
if not forge_script:
    raise RuntimeError('dashboard v4 forge script anchor missing')
html=html[:forge_script.end()]+script+html[forge_script.end():]
HTML.write_text(html)

# Expose the real current Stratum worker difficulty to the dashboard. With the
# solo setup there is normally one active worker; if none is active we fall
# back to the configured fixed difficulty.
text=APP.read_text()
if 'pool_difficulty=' not in text:
    marker='    active_workers=list(workers.keys())\n'
    insert='''    active_workers=list(workers.keys())\n    pool_difficulty=fixed_diff\n    for worker_name in active_workers:\n        worker_state=workers.get(worker_name,{})\n        worker_diff=as_number(worker_state.get("difficulty"),0)\n        if worker_diff>0:\n            pool_difficulty=worker_diff\n            break\n'''
    if marker not in text:
        raise RuntimeError('dashboard worker authority anchor missing')
    text=text.replace(marker,insert,1)

if '"pool_difficulty":pool_difficulty' not in text:
    marker='"fixed_difficulty":fixed_diff,'
    if marker not in text:
        raise RuntimeError('dashboard mining fixed_difficulty anchor missing')
    text=text.replace(marker,marker+'"pool_difficulty":pool_difficulty,"vardiff_mode":True,',1)
APP.write_text(text)

print('FIXCORE forge enforced: live VarDiff HUD hardened, legacy miner removed, and authoritative pool difficulty exposed')
