#!/usr/bin/env python3
"""Make forge metric cards use the exact accepted/rejected share-card plate treatment."""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()

css_link = '<link rel="stylesheet" href="/static/dashboard_v4_forge_metrics_bevel.css?v=20260823-2">'

# Idempotent: remove any previously injected version before inserting the current one.
html = re.sub(
    r'<link rel="stylesheet" href="/static/dashboard_v4_forge_metrics_bevel\.css\?v=[^"]+">',
    '',
    html,
)

anchor = re.search(
    r'<link rel="stylesheet" href="/static/dashboard_v4_forge_metrics_layout\.css\?v=[^"]+">',
    html,
)
if not anchor:
    raise RuntimeError('dashboard v4 metrics layout stylesheet anchor missing')

html = html[:anchor.end()] + css_link + html[anchor.end():]
HTML.write_text(html)

print('dashboard forge metrics bevel patch: HASHRATE and SHARES/MIN now use the exact accepted/rejected share-card plate treatment')
