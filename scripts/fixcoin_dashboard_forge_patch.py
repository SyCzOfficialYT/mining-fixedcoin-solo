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
# Remove the old anvil/impact markup if an older patch inserted it.
html=re.sub(r'\s*<div class="anvil"[^>]*>.*?</div>\s*<div class="impact"[^>]*>.*?</div>', '', html, count=1, flags=re.S)
if 'id="forgeCore"' not in html:
    raise RuntimeError('FIXCORE mount missing after legacy miner cleanup')
if 'dashboard_v4_miner.js' in html or 'miner-reference' in html or '<img' in html or '<image' in html:
    raise RuntimeError('legacy miner markup survived FIXCORE dashboard patch')

# Live VarDiff HUD: show the actual current worker/pool difficulty, never the
# decorative "VarDiff" placeholder used by the old reference composition.
css_link='<link rel="stylesheet" href="/static/dashboard_v4_forge_hud.css?v=20260823-2">'
# Replace an older generated link if the patch has already run in a working tree.
html=re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_forge_hud\.css\?v=[^"]+">', '', html)
anchor='<link rel="stylesheet" href="/static/dashboard_v4_shares_min.css?v=20260823-1">'
if anchor not in html:
    raise RuntimeError('dashboard v4 shares/min stylesheet anchor missing')
html=html.replace(anchor,anchor+css_link,1)

hud='<div class="forge-vardiff-hud" id="forgeVarDiff"><span>VARDIFF MODE</span><strong id="poolDiffValue">—</strong><small id="poolDiffLabel">POOL DIFF · LIVE</small></div>'
if 'id="poolDiffValue"' not in html:
    anchor='<div class="forge-vignette"></div>'
    if anchor not in html:
        raise RuntimeError('forge vignette anchor missing')
    html=html.replace(anchor,anchor+hud,1)

# Status dots are real children of the counters and are positioned by the
# forge HUD stylesheet in the bottom-right card corner. The stream markers are
# implementation-only and remain hidden by CSS.
html=html.replace('<div class="forge-counter accepted" id="acceptedCounter"><span>ACCEPTED SHARES</span>', '<div class="forge-counter accepted" id="acceptedCounter"><span>ACCEPTED SHARES</span>', 1)
html=html.replace('</div><div class="forge-counter rejected" id="rejectedCounter"><span>REJECTED SHARES</span>', '</div><div class="forge-counter rejected" id="rejectedCounter"><span>REJECTED SHARES</span>', 1)

script='<script defer src="/static/dashboard_v4_forge_hud.js?v=20260823-1"></script>'
if script not in html:
    html=html.replace('<script defer src="/static/dashboard_v4_forge.js?v=20260823-2"></script>', '<script defer src="/static/dashboard_v4_forge.js?v=20260823-2"></script>'+script, 1)
HTML.write_text(html)

# Expose the real current Stratum worker difficulty to the dashboard. With the
# solo setup there is normally one active worker; if none is active we fall
# back to the configured fixed difficulty. This patch intentionally anchors
# on the stable fixed_difficulty field rather than the complete JSON fragment,
# because earlier dashboard patches may add fields beside it.
text=APP.read_text()
if 'pool_difficulty=' not in text:
    marker='    active_workers=list(workers.keys())\n'
    insert='''    active_workers=list(workers.keys())\n    pool_difficulty=fixed_diff\n    for worker_name in active_workers:\n        worker_state=workers.get(worker_name,{})\n        worker_diff=as_number(worker_state.get("difficulty"),0)\n        if worker_diff>0:\n            pool_difficulty=worker_diff\n            break\n'''
    if marker not in text:
        raise RuntimeError('dashboard worker authority anchor missing')
    text=text.replace(marker,insert,1)

# Add the live pool difficulty and explicit VarDiff mode without depending on
# the exact ordering of fields emitted by previous dashboard patches.
if '"pool_difficulty":pool_difficulty' not in text:
    marker='"fixed_difficulty":fixed_diff,'
    if marker not in text:
        raise RuntimeError('dashboard mining fixed_difficulty anchor missing')
    text=text.replace(marker,marker+'"pool_difficulty":pool_difficulty,"vardiff_mode":True,',1)
APP.write_text(text)

print('FIXCORE forge enforced: legacy miner removed, live VarDiff HUD wired, and share status dots/icons moved into counters')
