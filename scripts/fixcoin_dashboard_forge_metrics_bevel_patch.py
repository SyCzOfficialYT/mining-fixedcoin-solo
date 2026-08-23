#!/usr/bin/env python3
"""Make forge metric cards use the same soft neon-bevel treatment as share cards."""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()

css_link = '<link rel="stylesheet" href="/static/dashboard_v4_forge_metrics_bevel.css?v=20260823-1">'

# Idempotent: remove an older version before inserting the canonical link.
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

print('dashboard forge metrics bevel patch: HASHRATE and SHARES/MIN now share the accepted/rejected card bevel language')
