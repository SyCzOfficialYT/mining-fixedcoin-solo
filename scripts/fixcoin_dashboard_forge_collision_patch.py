#!/usr/bin/env python3
"""Apply the central particle-collision/neon layer after the final Forge visual patch."""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()
VERSION = '20260823-1'
CSS = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_collision.css?v={VERSION}">'

# Replace the old share-impact cache-buster so the central collision engine is loaded.
html = re.sub(r'/static/dashboard_v4_share_impact\.js\?v=[0-9-]+', f'/static/dashboard_v4_share_impact.js?v={VERSION}', html)

# Inject collision CSS immediately after the final Forge transparency layer when present.
for pattern in (
    r'<link rel="stylesheet" href="/static/dashboard_v4_forge_collision\.css\?v=[^"]+">',
):
    html = re.sub(pattern, '', html)
anchor = '/static/dashboard_v4_forge_transparency.css?v=20260823-7'
if anchor in html:
    html = html.replace(f'<link rel="stylesheet" href="{anchor}">', f'<link rel="stylesheet" href="{anchor}">' + CSS, 1)
else:
    metrics = '<link rel="stylesheet" href="/static/dashboard_v4_forge_metrics_layout.css?v=20260823-1">'
    if metrics not in html:
        raise RuntimeError('forge metrics stylesheet anchor missing')
    html = html.replace(metrics, metrics + CSS, 1)

required = [
    'dashboard_v4_forge_collision.css',
    '/static/dashboard_v4_share_impact.js?v=20260823-1',
    'class="forge-rock rock-left"',
    'class="forge-rock rock-right"',
    'id="acceptedCounter"',
    'id="rejectedCounter"',
]
missing = [x for x in required if x not in html]
if missing:
    raise RuntimeError('forge collision patch verification failed: ' + ', '.join(missing))

HTML.write_text(html)
print('dashboard collision patch applied: central-only event particles, collision-driven counter neon, directional streams disabled, mountains lowered')
