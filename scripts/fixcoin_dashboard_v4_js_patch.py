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

required = [
    'function render(s,animate=false){', 'async function poll(animate=false){',
    "new EventSource('/api/stream')", 'function burstParticles(', 'function strike(',
    'started_epoch', "if(e.type==='accept')", "if(e.type==='reject')", 'particleCanvas', 'spawnParticle(',
]
missing = [item for item in required if item not in text]

# Modern v4 may use the compositor canvas instead of the legacy HTML marker.
# Accept either the legacy particle canvas or the current compositor layers.
html_required = [
    'forge-core-wrap', 'id="forgeCore"', 'id="forgeParticleField"',
    'dashboard_v4_forge.css', 'id="acceptedCounter"', 'id="rejectedCounter"',
]
missing += [item for item in html_required if item not in html]

modern_particle_layers = (
    'fx-animation-canvas' in html
    and 'candidate-particle-canvas' in html
)
if 'particle-canvas' not in html and not modern_particle_layers:
    missing.append('particle-canvas|fx-animation-canvas+candidate-particle-canvas')

forge_required = [
    'fixedcoin:accept', 'fixedcoin:reject', 'fixedcoin:block',
    'hit-accept', 'hit-reject', 'hit-block',
]
missing += [item for item in forge_required if item not in forge_js]

css_required = ['.forge-core{', '.core-energy{', '.forge-ring{', '.forge.hit-accept', '.forge.hit-reject']
missing += [item for item in css_required if item not in forge_css]
if '.particle-canvas' not in forge_css and not any(
    token in forge_css for token in ('fx-animation-canvas', 'candidate-particle-canvas')
):
    missing.append('.particle-canvas|modern compositor canvas')

if missing:
    raise RuntimeError(
        'dashboard v4 is missing required realtime/FIXCORE primitives: '
        + ', '.join(missing)
    )

for forbidden in ('miner_reference.svg', '<img', '<image', 'dashboard_v4_miner.js'):
    if forbidden in html:
        raise RuntimeError('legacy miner primitive found in dashboard template: ' + forbidden)

print(
    'dashboard v4 verified: SSE, authoritative timer, FIXCORE SVG energy forge, '
    'realtime canvas particles, accept/reject/block motion, and no legacy miner markup'
)
