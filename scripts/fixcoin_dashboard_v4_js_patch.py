#!/usr/bin/env python3
"""Validate the canonical v4 dashboard JS without relying on obsolete anchors."""
from pathlib import Path

JS = Path('/app/monitor/static/dashboard_v4.js')
text = JS.read_text()
required = [
    'function render(s,animate=false){',
    'async function poll(animate=false){',
    "new EventSource('/api/stream')",
    'poll(true)',
]
missing = [item for item in required if item not in text]
if missing:
    raise RuntimeError('dashboard v4 JS is missing required realtime primitives: ' + ', '.join(missing))
print('dashboard v4 JS verified: realtime render, SSE bridge, and animated event flow present')
