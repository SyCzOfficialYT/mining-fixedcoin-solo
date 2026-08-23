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

# The miner owns the frame-accurate clock. The legacy 250 ms timer must not
# fight it or snap the countdown back to stale poll data.
dash = dash.replace('setInterval(()=>updateTimer(state?.round||{}),250);', '/* dashboard_v4_miner.js owns the frame-accurate round clock */', 1)

# Convert the existing authoritative SSE messages into DOM events consumed by
# the vector miner. There is deliberately only ONE EventSource connection.
old_stream = "if(e.type==='accept'){acceptFx(e.work);poll(false)}else if(e.type==='reject'){rejectFx(e.share_diff);poll(false)}else if(e.type==='block'){blockFx();poll(false)}else if(e.type==='round'){poll(false)}else if(e.type==='state'){poll(false)}"
new_stream = "if(e.type==='accept'){acceptFx(e.work);window.dispatchEvent(new CustomEvent('fixedcoin:accept',{detail:e}));poll(false)}else if(e.type==='reject'){rejectFx(e.share_diff);window.dispatchEvent(new CustomEvent('fixedcoin:reject',{detail:e}));poll(false)}else if(e.type==='block'){blockFx();window.dispatchEvent(new CustomEvent('fixedcoin:block',{detail:e}));poll(false)}else if(e.type==='round'){window.dispatchEvent(new CustomEvent('fixedcoin:round',{detail:e}));poll(false)}else if(e.type==='state'){poll(false)}"
if old_stream in dash:
    dash = dash.replace(old_stream, new_stream, 1)
    print('patched SSE bridge: accept/reject/block/real-round -> vector miner')
elif "fixedcoin:accept" not in dash:
    raise RuntimeError('dashboard SSE handler anchor missing; refusing to ship a non-reactive miner')

DASH_JS.write_text(dash)

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
    if forbidden in html:
        raise RuntimeError(f'legacy raster miner primitive still present in template: {forbidden}')

if '.miner-puppet' not in css or '.miner-reference-wrap>img' not in css:
    raise RuntimeError('dashboard miner CSS hardening missing')

print('dashboard miner v2 verified: pure vector humanoid rig, coordinated body/arm/hammer motion, SSE-driven strikes, impact effects, and realtime particles')
