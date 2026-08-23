#!/usr/bin/env python3
"""Apply the final Forge geometry, HUD layers, and collision layer after the base dashboard patches."""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()
VERSION = '20260823-15'
COLLISION_CSS = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_collision.css?v={VERSION}">'
COLLISION_JS = f'<script defer src="/static/dashboard_v4_forge_collision.js?v={VERSION}"></script>'
HUD_CSS = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_hud_match.css?v={VERSION}">'
REFERENCE_CSS = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_reference_final.css?v={VERSION}">'
CANDIDATE_CSS = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_candidate_restore.css?v={VERSION}">'
METRICS_CSS = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_metrics_match.css?v={VERSION}">'

html = re.sub(r'<script[^>]+/static/dashboard_v4_share_impact\.js\?v=[^>]+></script>', '', html)
for pattern in (
    r'<link rel="stylesheet" href="/static/dashboard_v4_forge_collision\.css\?v=[^"]+">',
    r'<script[^>]+dashboard_v4_forge_collision\.js\?v=[^>]+></script>',
    r'<link rel="stylesheet" href="/static/dashboard_v4_forge_hud_match\.css\?v=[^"]+">',
    r'<link rel="stylesheet" href="/static/dashboard_v4_forge_reference_final\.css\?v=[^"]+">',
    r'<link rel="stylesheet" href="/static/dashboard_v4_forge_candidate_restore\.css\?v=[^"]+">',
    r'<link rel="stylesheet" href="/static/dashboard_v4_forge_metrics_match\.css\?v=[^"]+">',
):
    html = re.sub(pattern, '', html)

anchor_match = re.search(r'<link rel="stylesheet" href="/static/dashboard_v4_forge_metrics_layout\.css\?v=[^"]+">', html)
if not anchor_match:
    raise RuntimeError('forge metrics stylesheet anchor missing')
anchor = anchor_match.group(0)
html = html.replace(anchor, anchor + COLLISION_CSS + HUD_CSS + REFERENCE_CSS + CANDIDATE_CSS + METRICS_CSS, 1)

parallax = re.search(r'(<script defer src="/static/dashboard_v4_share_parallax\.js\?v=[^"]+"></script>)', html)
if not parallax:
    raise RuntimeError('dashboard share parallax script anchor missing')
html = html.replace(parallax.group(1), parallax.group(1) + COLLISION_JS, 1)

required = [
    'dashboard_v4_forge_collision.css',
    'dashboard_v4_forge_collision.js',
    'dashboard_v4_forge_hud_match.css',
    'dashboard_v4_forge_reference_final.css',
    'dashboard_v4_forge_candidate_restore.css',
    'dashboard_v4_forge_metrics_match.css',
    'dashboard_v4_share_parallax.js',
    'class="forge-rock rock-left"',
    'class="forge-rock rock-right"',
    'id="acceptedCounter"',
    'id="rejectedCounter"',
]
missing = [x for x in required if x not in html]
if missing:
    raise RuntimeError('final Forge patch verification failed: ' + ', '.join(missing))
if '/static/dashboard_v4_share_impact.js?' in html:
    raise RuntimeError('legacy share-impact JS is still included; refusing to build conflicting particle engines')

HTML.write_text(html)
print('dashboard Forge reference match applied; integrated Block Candidate restored; left metrics aligned to Candidate/share-instrument family; per-particle collision layer loaded')
