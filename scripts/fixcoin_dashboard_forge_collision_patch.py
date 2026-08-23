#!/usr/bin/env python3
"""Apply the final per-particle collision/neon layer after the Forge visual patch."""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()
VERSION = '20260823-9'
CSS = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_collision.css?v={VERSION}">'
JS = f'<script defer src="/static/dashboard_v4_forge_collision.js?v={VERSION}"></script>'

# The legacy share-impact client owns a single burst-level glow and therefore
# fundamentally conflicts with the per-particle OFF/ON model. Remove the old
# client include completely; the CSS remains harmless, but the JS must not run.
html = re.sub(r'<script[^>]+/static/dashboard_v4_share_impact\.js\?v=[^>]+></script>', '', html)
# Remove any previous collision includes, regardless of cache-buster.
html = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_forge_collision\.css\?v=[^"]+">', '', html)
html = re.sub(r'<script[^>]+dashboard_v4_forge_collision\.js\?v=[^>]+></script>', '', html)

transparency_match = re.search(r'<link rel="stylesheet" href="/static/dashboard_v4_forge_transparency\.css\?v=[^"]+">', html)
if transparency_match:
    anchor = transparency_match.group(0)
    html = html.replace(anchor, anchor + CSS, 1)
else:
    metrics = re.search(r'<link rel="stylesheet" href="/static/dashboard_v4_forge_metrics_layout\.css\?v=[^"]+">', html)
    if not metrics:
        raise RuntimeError('forge metrics stylesheet anchor missing')
    anchor = metrics.group(0)
    html = html.replace(anchor, anchor + CSS, 1)

# The collision engine is the only source of share-event particles. Load it
# immediately after parallax so all geometry has settled before coordinates are read.
parallax = re.search(r'(<script defer src="/static/dashboard_v4_share_parallax\.js\?v=[^"]+"></script>)', html)
if not parallax:
    raise RuntimeError('dashboard share parallax script anchor missing')
html = html.replace(parallax.group(1), parallax.group(1) + JS, 1)

required = [
    'dashboard_v4_forge_collision.css',
    'dashboard_v4_forge_collision.js',
    'dashboard_v4_share_parallax.js',
    'class="forge-rock rock-left"',
    'class="forge-rock rock-right"',
    'id="acceptedCounter"',
    'id="rejectedCounter"',
]
missing = [x for x in required if x not in html]
if missing:
    raise RuntimeError('forge collision patch verification failed: ' + ', '.join(missing))

if '/static/dashboard_v4_share_impact.js?' in html:
    raise RuntimeError('legacy share-impact JS is still included; refusing to build conflicting particle engines')

HTML.write_text(html)
print('dashboard collision layer applied: legacy share-impact JS removed; each arriving particle owns its own OFF/ON neon pulse; centered progress field preserved')
