#!/usr/bin/env python3
"""Validate the canonical v4 dashboard realtime and FIXCORE forge primitives."""
from pathlib import Path

JS = Path('/app/monitor/static/dashboard_v4.js')
HTML = Path('/app/monitor/templates/dashboard_v4.html')
FORGE_JS = Path('/app/monitor/static/dashboard_v4_forge.js')
FORGE_CSS = Path('/app/monitor/static/dashboard_v4_forge.css')
text = JS.read_text()
html = HTML.read_text()
forge_js = FORGE_JS.read_text()
forge_css = FORGE_CSS.read_text()

# These are the canonical primitives used by the current v4 forge.  The old
# forge-dust DOM particle emitter was intentionally removed; keeping it here
# made the validator reject the newer particle-canvas implementation during
# Docker builds even though the dashboard itself was valid.
required = [
    'function render(s,animate=false){', 'async function poll(animate=false){',
    "new EventSource('/api/stream')", 'function burstParticles(', 'function strike(',
    'started_epoch', "if(e.type==='accept')", "if(e.type==='reject')", 'particleCanvas', 'spawnParticle(',
]
missing = [item for item in required if item not in text]

html_required = [
    'forge-core-wrap', 'id="forgeCore"', 'id="forgeParticleField"',
    'particle-canvas', 'dashboard_v4_forge.css', 'id="acceptedCounter"',
    'id="rejectedCounter"',
]
missing += [item for item in html_required if item not in html]

# FIXCORE owns the share-impact state.  Do not require the removed legacy
# forge-dust primitive; require the actual event-driven forge hooks instead.
forge_required = [
    'fixedcoin:accept', 'fixedcoin:reject', 'fixedcoin:block',
    'hit-accept', 'hit-reject', 'hit-block',
]
missing += [item for item in forge_required if item not in forge_js]

css_required = [
    '.forge-core{', '.core-energy{', '.forge-ring{',
    '.forge.hit-accept', '.forge.hit-reject', '.particle-canvas',
]
missing += [item for item in css_required if item not in forge_css]

if missing:
    raise RuntimeError(
        'dashboard v4 is missing required realtime/FIXCORE primitives: '
        + ', '.join(missing)
    )

for forbidden in (
    'miner_reference.svg', '<img', '<image', 'dashboard_v4_miner.js',
):
    if forbidden in html:
        raise RuntimeError('legacy miner primitive found in dashboard template: ' + forbidden)

print(
    'dashboard v4 verified: SSE, authoritative timer, FIXCORE SVG energy forge, '
    'realtime canvas particles, accept/reject/block motion, and no legacy miner markup'
)
