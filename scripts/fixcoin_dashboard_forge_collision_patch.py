#!/usr/bin/env python3
"""Apply the final central particle-collision/neon layer after the Forge visual patch."""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()
VERSION = '20260823-1'
CSS = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_collision.css?v={VERSION}">'

# Remove any previous collision include, regardless of its cache-buster.
html = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_forge_collision\.css\?v=[^"]+">', '', html)

# The Forge upgrade patch owns the transparency stylesheet version. Do not hard-code
# that version here: the two patches are intentionally independent and may bump their
# cache-busters at different times.
transparency_match = re.search(r'<link rel="stylesheet" href="/static/dashboard_v4_forge_transparency\.css\?v=[^"]+">', html)
if transparency_match:
    anchor = transparency_match.group(0)
    html = html.replace(anchor, anchor + CSS, 1)
else:
    # Safe fallback for builds where the transparency layer is absent: load the
    # collision layer after the forge metrics stylesheet so it still wins over
    # the legacy share-impact rules.
    metrics = re.search(r'<link rel="stylesheet" href="/static/dashboard_v4_forge_metrics_layout\.css\?v=[^"]+">', html)
    if not metrics:
        raise RuntimeError('forge metrics stylesheet anchor missing')
    anchor = metrics.group(0)
    html = html.replace(anchor, anchor + CSS, 1)

# Make the central collision layer the last share-impact JS version.
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
