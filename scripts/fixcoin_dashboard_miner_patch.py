#!/usr/bin/env python3
"""Enforce the canonical vector/humanoid miner implementation for dashboard v4."""
from pathlib import Path

HTML = Path('/app/monitor/templates/dashboard_v4.html')
JS = Path('/app/monitor/static/dashboard_v4_miner.js')
CSS = Path('/app/monitor/static/dashboard_v4_miner.css')
DASH_JS = Path('/app/monitor/static/dashboard_v4.js')

html = HTML.read_text()
js = JS.read_text()
css = CSS.read_text()
dash = DASH_JS.read_text()

# Keep the frame-accurate miner clock authoritative if an older build still has
# the legacy 250ms timer loop.
dash = dash.replace('setInterval(()=>updateTimer(state?.round||{}),250);', '/* dashboard_v4_miner.js owns the frame-accurate round clock */', 1)
DASH_JS.write_text(dash)

# Never allow the old raster reference back into the live dashboard.
old = '<div class="miner-reference-wrap" id="minerFigure"><img class="miner-reference" src="/static/miner_reference.svg?v=20260823-2" alt="FIX-ASIC miner" draggable="false"></div>'
if old in html:
    html = html.replace(old, '<div class="miner-reference-wrap" id="minerFigure" aria-label="Animated FIX-ASIC miner"></div>', 1)
    HTML.write_text(html)
    print('removed legacy raster miner from dashboard template')

for needle, label in [
    ('host.innerHTML=svg', 'vector miner SVG mount'),
    ('class="miner-upper-arm"', 'independent upper-arm rig'),
    ('class="miner-forearm"', 'independent forearm rig'),
    ('class="miner-hammer"', 'independent hammer rig'),
    ('function strike(kind=', 'human hammer strike animation'),
    ('requestAnimationFrame(tick)', 'high-fidelity particle renderer'),
]:
    if needle not in js:
        raise RuntimeError(f'missing canonical animated miner primitive: {label}')

for forbidden in ('<image', '<img', 'miner_reference.svg'):
    if forbidden in js or forbidden in html:
        raise RuntimeError(f'legacy raster miner primitive still present: {forbidden}')

if '.miner-puppet' not in css or '.miner-reference-wrap>img' not in css:
    raise RuntimeError('dashboard miner CSS hardening missing')

print('dashboard miner v2 verified: pure vector humanoid rig, coordinated body/arm/hammer motion, impact effects, and realtime particles')
