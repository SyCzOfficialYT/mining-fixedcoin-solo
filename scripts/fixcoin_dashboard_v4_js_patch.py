#!/usr/bin/env python3
"""Validate the canonical v4 dashboard realtime and vector-miner primitives."""
from pathlib import Path

JS = Path('/app/monitor/static/dashboard_v4.js')
HTML = Path('/app/monitor/templates/dashboard_v4.html')
MINER = Path('/app/monitor/static/dashboard_v4_miner.js')
text = JS.read_text()
html = HTML.read_text()
miner = MINER.read_text()
required = [
    'function render(s,animate=false){',
    'async function poll(animate=false){',
    "new EventSource('/api/stream')",
    'function burstParticles(',
    'function strike(',
    'started_epoch',
    "if(e.type==='accept')",
    "if(e.type==='reject')",
    'particleCanvas',
    'spawnParticle(',
]
missing = [item for item in required if item not in text]
html_required = ['miner-reference-wrap','id="minerFigure"','particle-canvas']
missing += [item for item in html_required if item not in html]
miner_required = ['host.innerHTML=svg','miner-upper-arm','miner-forearm','miner-hammer','function strike(kind=','requestAnimationFrame(tick)']
missing += [item for item in miner_required if item not in miner]
if missing:
    raise RuntimeError('dashboard v4 is missing required realtime/vector primitives: ' + ', '.join(missing))
for forbidden in ('miner_reference.svg','<img','<image'):
    if forbidden in html:
        raise RuntimeError('legacy raster miner primitive found in dashboard template: ' + forbidden)
print('dashboard v4 verified: SSE, authoritative timer, pure vector humanoid miner, strike rig, and realtime particle renderer present')
