#!/usr/bin/env python3
"""Validate the canonical v4 dashboard JS realtime/animation primitives."""
from pathlib import Path

JS = Path('/app/monitor/static/dashboard_v4.js')
HTML = Path('/app/monitor/templates/dashboard_v4.html')
text = JS.read_text()
html = HTML.read_text()
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
html_required = ['miner-reference-wrap','miner-reference','/static/miner_reference.svg','particle-canvas']
missing += [item for item in html_required if item not in html]
if missing:
    raise RuntimeError('dashboard v4 is missing required realtime/reference primitives: ' + ', '.join(missing))
print('dashboard v4 JS verified: SSE, authoritative timer, reference miner asset, strike animation, and canvas particle renderer present')
