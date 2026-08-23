#!/usr/bin/env python3
"""Validate the canonical v4 dashboard JS realtime/animation primitives."""
from pathlib import Path

JS = Path('/app/monitor/static/dashboard_v4.js')
text = JS.read_text()
required = [
    'function render(s,animate=false){',
    'async function poll(animate=false){',
    "new EventSource('/api/stream')",
    'function burstParticles(',
    'function strike(',
    'started_epoch',
    "if(e.type==='accept')",
    "if(e.type==='reject')",
]
missing = [item for item in required if item not in text]
if missing:
    raise RuntimeError('dashboard v4 JS is missing required realtime/animation primitives: ' + ', '.join(missing))
print('dashboard v4 JS verified: SSE, direct share animation, authoritative timer fields, and render path present')
