#!/usr/bin/env python3
"""Load the final explicit 3-row/5-row metric geometry after the main reference layer."""
from pathlib import Path
import re

HTML=Path('/app/monitor/templates/dashboard_v4.html')
s=HTML.read_text()
link='<link rel="stylesheet" href="/static/dashboard_v4_reference_rows.css?v=20260825-1">'
s=re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_reference_rows\.css\?v=[^"]+">','',s)
anchor='<link rel="stylesheet" href="/static/dashboard_v4_reference_rebuild.css?v=20260825-1">'
if anchor not in s:
    raise RuntimeError('reference rows patch: rebuild stylesheet anchor missing')
s=s.replace(anchor,anchor+link,1)
HTML.write_text(s)
print('dashboard reference rows patch applied: 3 primary + 5 balance/rate cards with explicit gaps')
