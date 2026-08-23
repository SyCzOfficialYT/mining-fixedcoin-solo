#!/usr/bin/env python3
"""Validate the canonical v4 dashboard realtime and FIXCORE forge primitives."""
from pathlib import Path

JS = Path('/app/monitor/static/dashboard_v4.js')
HTML = Path('/app/monitor/templates/dashboard_v4.html')
FORGE_JS = Path('/app/monitor/static/dashboard_v4_forge.js')
FORGE_CSS = Path('/app/monitor/static/dashboard_v4_forge.css')
text = JS.read_text(); html = HTML.read_text(); forge_js = FORGE_JS.read_text(); forge_css = FORGE_CSS.read_text()
required = [
    'function render(s,animate=false){', 'async function poll(animate=false){',
    "new EventSource('/api/stream')", 'function burstParticles(', 'function strike(',
    'started_epoch', "if(e.type==='accept')", "if(e.type==='reject')", 'particleCanvas', 'spawnParticle(',
]
missing = [item for item in required if item not in text]
html_required = ['forge-core-wrap','id="forgeCore"','id="forgeParticleField"','particle-canvas','dashboard_v4_forge.css']
missing += [item for item in html_required if item not in html]
forge_required = ['fixedcoin:accept','fixedcoin:reject','fixedcoin:block','hit-accept','hit-reject','forge-dust']
missing += [item for item in forge_required if item not in forge_js]
css_required = ['.forge-core{','.core-energy{','.core-ring','.forge.hit-accept','.forge.hit-reject']
missing += [item for item in css_required if item not in forge_css]
if missing:
    raise RuntimeError('dashboard v4 is missing required realtime/FIXCORE primitives: ' + ', '.join(missing))
for forbidden in ('miner_reference.svg','<img','<image','dashboard_v4_miner.js'):
    if forbidden in html:
        raise RuntimeError('legacy miner primitive found in dashboard template: ' + forbidden)
print('dashboard v4 verified: SSE, authoritative timer, FIXCORE SVG energy forge, realtime particles, accept/reject/block motion, and no legacy miner markup')
