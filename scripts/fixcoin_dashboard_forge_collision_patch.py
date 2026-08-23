#!/usr/bin/env python3
"""Apply the final central particle-collision/neon layer after the Forge visual patch."""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()
VERSION = '20260823-1'
CSS = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_collision.css?v={VERSION}">'

html = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_forge_collision\.css\?v=[^"]+">', '', html)
anchor = '<link rel="stylesheet" href="/static/dashboard_v4_forge_transparency.css?v=20260823-7">'
if anchor not in html:
    raise RuntimeError('forge transparency stylesheet anchor missing')
html = html.replace(anchor, anchor + CSS, 1)
html = re.sub(r'/static/dashboard_v4_share_impact\.js\?v=[0-9-]+', f'/static/dashboard_v4_share_impact.js?v={VERSION}', html)

required = [
    'dashboard_v4_forge_collision.css',
    f'/static/dashboard_v4_share_impact.js?v={VERSION}',
    'class="forge-rock rock-left"',
    'class="forge-rock rock-right"',
    'id="acceptedCounter"',
    'id="rejectedCounter"',
]
missing = [x for x in required if x not in html]
if missing:
    raise RuntimeError('forge collision patch verification failed: ' + ', '.join(missing))

HTML.write_text(html)
print('dashboard collision layer applied: center-only particles, collision-driven neon, disabled directional streams, lowered mountains')
