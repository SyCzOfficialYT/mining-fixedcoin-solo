#!/usr/bin/env python3
"""Final visual polish after all reference composition patches.

The reference Block Candidate is a dedicated proof-of-work proximity HUD.
It contains the title, best-share percentage, progress track, next height and
its right-hand FIXCORE plate. Recent Activity is intentionally not part of
this surface.
"""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()

css = '<link rel="stylesheet" href="/static/dashboard_v4_reference_polish.css?v=20260825-3">'
html = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_reference_polish\.css\?v=[^"]+">', '', html)
html = html.replace('</head>', css + '</head>', 1)

# Older reference patches may have inserted the activity panel into the
# candidate. The reference does not contain that feed, so remove the exact
# known markup while keeping the candidate telemetry IDs untouched.
activity = '''<div class="activity-panel"><div class="activity-title">RECENT ACTIVITY</div><div id="activityList"><div class="activity-empty">Waiting for live shares…</div></div></div>'''
html = html.replace(activity, '', 1)

HTML.write_text(html)
print('dashboard reference polish applied: complete candidate HUD + no activity feed')
