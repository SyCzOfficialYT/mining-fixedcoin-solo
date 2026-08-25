#!/usr/bin/env python3
"""Final isolated Block Candidate composition for dashboard v4.

The candidate is deliberately kept outside the Forge DOM so Forge positioning rules
cannot distort it. Existing telemetry IDs are preserved.
"""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()

CSS = '<link rel="stylesheet" href="/static/dashboard_v4_candidate_final.css?v=20260825-1">'
html = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_candidate_final\.css\?v=[^"]+">', '', html)
head = html.find('</head>')
if head < 0:
    raise RuntimeError('candidate final: </head> not found')
html = html[:head] + CSS + html[head:]

candidate_start = html.find('<section class="candidate panel" id="candidate">')
if candidate_start < 0:
    raise RuntimeError('candidate final: candidate section not found')

stats_start = html.find('<section class="stats-grid">', candidate_start)
if stats_start < 0:
    raise RuntimeError('candidate final: stats section not found')

# Candidate is a direct section in the current template. Remove any activity panel
# nested in it without touching the candidate section boundary.
activity_start = html.find('<div class="activity-panel">', candidate_start, stats_start)
if activity_start >= 0:
    activity_end = html.find('</div>', activity_start)
    if activity_end < 0:
        raise RuntimeError('candidate final: activity block closing tag not found')
    activity_end += len('</div>')
    html = html[:activity_start] + html[activity_end:]
    stats_start = html.find('<section class="stats-grid">', candidate_start)

# If an older patch moved candidate into Forge, extract the complete candidate section
# and place it immediately before stats-grid. This is the key structural normalization.
forge_start = html.find('<section class="forge panel" id="forge">')
if forge_start >= 0 and candidate_start > forge_start and candidate_start < stats_start:
    candidate_end = html.find('</section>', candidate_start)
    if candidate_end < 0 or candidate_end > stats_start:
        raise RuntimeError('candidate final: candidate closing tag not found')
    candidate_end += len('</section>')
    candidate = html[candidate_start:candidate_end]
    html = html[:candidate_start] + html[candidate_end:]
    stats_start = html.find('<section class="stats-grid">')
    if stats_start < 0:
        raise RuntimeError('candidate final: stats marker lost after extraction')
    html = html[:stats_start] + candidate + html[stats_start:]

HTML.write_text(html)
print('dashboard candidate final applied: isolated candidate section + final HUD stylesheet')
