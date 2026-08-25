#!/usr/bin/env python3
"""Final visual polish after all reference composition patches.
Restores the reference candidate activity surface and applies the final responsive metric geometry.
"""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()

css = '<link rel="stylesheet" href="/static/dashboard_v4_reference_polish.css?v=20260825-2">'
html = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_reference_polish\.css\?v=[^"]+">', '', html)
html = html.replace('</head>', css + '</head>', 1)

# Reference candidate contains Recent Activity below the two-column candidate instrument.
if 'class="activity-panel"' not in html:
    activity = '''<div class="activity-panel"><div class="activity-title">RECENT ACTIVITY</div><div id="activityList"><div class="activity-empty">Waiting for live shares…</div></div></div>'''
    marker = '</section><section class="stats-grid">'
    if marker not in html:
        raise RuntimeError('reference polish: candidate/stats boundary not found')
    html = html.replace(marker, activity + marker, 1)

HTML.write_text(html)
print('dashboard reference polish applied: restored candidate activity + final responsive metric geometry')
