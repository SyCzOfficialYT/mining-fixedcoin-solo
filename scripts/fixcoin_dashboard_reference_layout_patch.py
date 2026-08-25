#!/usr/bin/env python3
"""Apply the reference dashboard layout without touching mining telemetry."""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
h = HTML.read_text()

# Remove an older copy/version if present, then install the current layout CSS.
h = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_reference_layout\.css\?v=[^"]+">', '', h)
css = '<link rel="stylesheet" href="/static/dashboard_v4_reference_layout.css?v=20260825-1">'
pos = h.find('</head>')
if pos < 0:
    raise RuntimeError('reference layout: </head> missing')
h = h[:pos] + css + h[pos:]

# Preserve the existing telemetry DOM. The current dashboard already exposes
# 3 primary stats followed by 4 balances + ETA, which is exactly the desired
# 3 + 5 reference card arrangement.
required = [
    '<section class="forge panel" id="forge">',
    '<section class="candidate panel" id="candidate">',
    '<section class="stats-grid">',
    'id="forgeHashrate"', 'id="sharesMin"',
    'id="acceptedCount"', 'id="rejectedCount"',
    'id="candidatePct"', 'id="candidateMeter"',
    'id="balanceConfirmed"', 'id="balanceUnconfirmed"',
    'id="balanceImmature"', 'id="balanceTotal"', 'id="eta"',
]
missing = [x for x in required if x not in h]
if missing:
    raise RuntimeError('reference layout: missing telemetry primitives: ' + ', '.join(missing))

HTML.write_text(h)
print('dashboard reference layout applied: 3-column forge, persistent FIXCORE, candidate particles, 3+5 metric grid, responsive mobile layout')
