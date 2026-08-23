#!/usr/bin/env python3
"""Make dashboard v4 effects/SSE wiring compatible and idempotent."""
from pathlib import Path

JS = Path('/app/monitor/static/dashboard_v4.js')
text = JS.read_text()
changed = False


def replace_once(old: str, new: str, label: str) -> None:
    global text, changed
    if old in text:
        text = text.replace(old, new, 1)
        changed = True
        print(f'patched dashboard v4 JS: {label}')
    else:
        print(f'dashboard v4 JS: {label} already patched or not applicable')


# Render accepts an explicit animation flag. This makes SSE-triggered renders
# animate while ordinary status polling stays visually quiet.
if 'function render(s,animate=false){' not in text:
    replace_once('function render(s){', 'function render(s,animate=false){', 'render animation flag')

replace_once('if(valid>lastAccepted){', 'if(animate&&valid>lastAccepted){', 'accept animation gate')
replace_once('if(bad>lastRejected){', 'if(animate&&bad>lastRejected){', 'reject animation gate')
replace_once(
    "if(progress>=100)flash($('candidate'),'explode',1800);",
    "if(animate&&progress>=100)flash($('candidate'),'explode',1800);",
    'block-candidate animation gate',
)

# Polling is still authoritative but does not replay animations.
replace_once(
    'if(r.ok)render(await r.json())',
    'if(r.ok)render(await r.json(),false)',
    'poll render without replaying effects',
)

# Real-time bridge: backend SSE is the event trigger; one status fetch keeps
# counters and all displayed values authoritative. EventSource reconnects.
if 'new EventSource(\'/api/stream\')' not in text and 'new EventSource("/api/stream")' not in text:
    marker = 'setInterval(()=>updateTimer(state?.round||{}),250);'
    sse = """setInterval(()=>updateTimer(state?.round||{}),250);
const stream=new EventSource('/api/stream');
stream.onmessage=()=>poll(true);
stream.onerror=()=>{};"""
    if marker not in text:
        raise RuntimeError('missing required dashboard v4 timer anchor')
    text = text.replace(marker, sse, 1)
    changed = True
    print('patched dashboard v4 JS: EventSource /api/stream bridge')
else:
    print('dashboard v4 JS: EventSource already present')

# poll() accepts whether the status refresh should animate.
if 'async function poll(animate=false){' not in text:
    replace_once('async function poll(){', 'async function poll(animate=false){', 'poll animation argument')
replace_once(
    'if(r.ok)render(await r.json(),false)',
    'if(r.ok)render(await r.json(),animate)',
    'poll forwards animation flag',
)

if changed:
    JS.write_text(text)

print('dashboard v4 JS patch complete: idempotent realtime animation/SSE wiring')
