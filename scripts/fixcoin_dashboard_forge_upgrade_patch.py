#!/usr/bin/env python3
"""Apply the final FIXCOIN forge/proximity visual layer after all base dashboard patches."""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()

CSS = '<link rel="stylesheet" href="/static/dashboard_v4_forge_upgrade.css?v=20260823-1">'
JS = '<script defer src="/static/dashboard_v4_forge_upgrade.js?v=20260823-1"></script>'

# Inject exactly once. The script intentionally runs late so it observes the
# authoritative dashboard_v4 realtime client instead of opening a second API/SSE flow.
html = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_forge_upgrade\.css\?v=[^"]+">', '', html)
html = re.sub(r'<script[^>]+dashboard_v4_forge_upgrade\.js\?v=[^>]+></script>', '', html)

anchor = '<link rel="stylesheet" href="/static/dashboard_v4_forge_metrics_layout.css?v=20260823-1">'
if anchor not in html:
    raise RuntimeError('dashboard forge metrics stylesheet anchor missing')
html = html.replace(anchor, anchor + CSS, 1)

anchor_js = '<script defer src="/static/dashboard_v4_share_parallax.js?v=20260823-9"></script>'
if anchor_js not in html:
    raise RuntimeError('dashboard forge client anchor missing')
html = html.replace(anchor_js, anchor_js + JS, 1)

# Fail the image build if the final realtime forge/proximity primitives disappear.
# The forge element also carries the panel class, so verify it as a token rather
# than requiring the impossible exact string class="forge".
required = [
    'class="forge panel"',
    'id="forgeStage"',
    'id="forgeCore"',
    'id="candidatePct"',
    'class="candidate-track"',
    'dashboard_v4_forge_upgrade.css',
    'dashboard_v4_forge_upgrade.js',
]
missing = [x for x in required if x not in html]
if missing:
    raise RuntimeError('dashboard forge upgrade verification failed: ' + ', '.join(missing))

HTML.write_text(html)
print('dashboard forge upgrade applied: continuous 0.001% progress particles, FIXCORE charge field, candidate conduit, and block-found choreography')
