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
html = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_candidate_final\\.css\\?v=[^"]+">', '', html)
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


def remove_div_block(source: str, start: int) -> str:
    """Remove one complete <div> subtree using balanced div tags."""
    open_tag = source.find('<div', start)
    if open_tag != start:
        raise RuntimeError('candidate final: activity div start invalid')

    depth = 0
    pos = start
    while pos < len(source):
        next_open = source.find('<div', pos)
        next_close = source.find('</div>', pos)

        if next_close < 0:
            raise RuntimeError('candidate final: unclosed activity div')

        if next_open >= 0 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            pos = next_close + len('</div>')
            if depth == 0:
                return source[:start] + source[pos:]

    raise RuntimeError('candidate final: activity div boundary not found')


# Remove the COMPLETE activity panel. The old implementation removed only the
# first nested title div, leaving #activityList behind as a giant orphaned list.
activity_start = html.find('<div class="activity-panel">', candidate_start, stats_start)
if activity_start >= 0:
    html = remove_div_block(html, activity_start)
    stats_start = html.find('<section class="stats-grid">', candidate_start)
    if stats_start < 0:
        raise RuntimeError('candidate final: stats marker lost after activity removal')

# Defensive cleanup: if a previous patch already stripped the activity-panel
# wrapper but left the activityList subtree, remove that subtree as well.
activity_list_start = html.find('<div id="activityList">', candidate_start, stats_start)
if activity_list_start >= 0:
    html = remove_div_block(html, activity_list_start)

# If an older patch moved candidate into Forge, extract the complete candidate section
# and place it immediately before stats-grid. This is the key structural normalization.
forge_start = html.find('<section class="forge panel" id="forge">')
candidate_start = html.find('<section class="candidate panel" id="candidate">')
stats_start = html.find('<section class="stats-grid">', candidate_start)
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

# Hard assertion: the final candidate must not contain an activity host.
candidate_start = html.find('<section class="candidate panel" id="candidate">')
stats_start = html.find('<section class="stats-grid">', candidate_start)
if candidate_start < 0 or stats_start < 0:
    raise RuntimeError('candidate final: final candidate/stats markers missing')
if 'activityList' in html[candidate_start:stats_start] or 'activity-panel' in html[candidate_start:stats_start]:
    raise RuntimeError('candidate final: activity markup survived candidate normalization')

HTML.write_text(html)
print('dashboard candidate final applied: isolated candidate section + activity removed + final HUD stylesheet')
