#!/usr/bin/env python3
"""Final reference composition pass for dashboard v4.

Keeps the existing telemetry/IDs but rebuilds the visual composition around the supplied
reference: forge instruments, candidate card, explicit metric rows and separated balance cards.

This patch intentionally uses structural marker positions instead of fragile HTML regexes.
The dashboard template is generated/minified by earlier patches, so matching a complete
``</section><section ...>`` sequence is not reliable after those patches have run.
"""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()

CSS = '<link rel="stylesheet" href="/static/dashboard_v4_reference_rebuild.css?v=20260825-2">'
html = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_reference_rebuild\.css\?v=[^"]+">', '', html)
head = html.find('</head>')
if head < 0:
    raise RuntimeError('reference rebuild: </head> not found')
html = html[:head] + CSS + html[head:]

# Remove the legacy Recent Activity block but KEEP the candidate section closing tag.
# The previous implementation could accidentally couple the activity div and section
# boundary. Use the unique activity-panel marker and the candidate section marker.
activity_start = html.find('<div class="activity-panel">')
if activity_start >= 0:
    candidate_start_for_activity = html.rfind('<section class="candidate panel" id="candidate">', 0, activity_start)
    candidate_end_for_activity = html.find('</section>', activity_start)
    if candidate_start_for_activity < 0 or candidate_end_for_activity < 0:
        raise RuntimeError('reference rebuild: activity/candidate boundary not found')
    html = html[:activity_start] + html[candidate_end_for_activity:]

# Extract the complete combo and candidate blocks from the post-forge-patch DOM.
combo_start = html.find('<div class="combo" id="combo">')
if combo_start < 0:
    raise RuntimeError('reference rebuild: combo markup not found')
combo_end = html.find('</div>', combo_start)
if combo_end < 0:
    raise RuntimeError('reference rebuild: combo closing tag not found')
combo_end += len('</div>')
combo = html[combo_start:combo_end]

candidate_start = html.find('<section class="candidate panel" id="candidate">')
stats_start = html.find('<section class="stats-grid">', candidate_start)
if candidate_start < 0 or stats_start < 0:
    raise RuntimeError('reference rebuild: candidate/stats markers not found')
candidate_end = html.find('</section>', candidate_start)
if candidate_end < 0 or candidate_end > stats_start:
    raise RuntimeError('reference rebuild: candidate closing tag not found')
candidate_end += len('</section>')
candidate = html[candidate_start:candidate_end]

# Remove the extracted blocks from their original locations.
html = html[:combo_start] + html[combo_end:]
# combo removal shifts candidate; find it again rather than reusing stale indexes.
candidate_start = html.find('<section class="candidate panel" id="candidate">')
stats_start = html.find('<section class="stats-grid">', candidate_start)
if candidate_start < 0 or stats_start < 0:
    raise RuntimeError('reference rebuild: candidate/stats markers lost after combo extraction')
candidate_end = html.find('</section>', candidate_start)
if candidate_end < 0 or candidate_end > stats_start:
    raise RuntimeError('reference rebuild: candidate closing tag lost after combo extraction')
candidate_end += len('</section>')
html = html[:candidate_start] + html[candidate_end:]

# Locate the forge and stats sections by their unique IDs/classes. Do not depend on
# the exact closing-tag adjacency because preceding patches may inject markup.
forge_start = html.find('<section class="forge panel" id="forge">')
stats_start = html.find('<section class="stats-grid">', forge_start)
if forge_start < 0 or stats_start < 0:
    raise RuntimeError('reference rebuild: forge/stats markers not found')

forge_body = html[forge_start:stats_start]
forge_close = forge_body.rfind('</section>')
if forge_close < 0:
    raise RuntimeError('reference rebuild: forge closing tag not found')

# Insert combo + candidate directly before the forge's closing tag.
forge_rebuilt = forge_body[:forge_close] + combo + candidate + forge_body[forge_close:]
html = html[:forge_start] + forge_rebuilt + html[stats_start:]

# Rebuild the lower metrics as two explicit rows: 3 mining metrics, then 5 wallet/rate cards.
stats = '''<section class="stats-grid">
<div class="stats-row stats-primary">
  <div class="stat panel"><span>AVG. SHARE DIFFICULTY</span><strong id="avgDiff">—</strong><small>(Last 10 min)</small><svg viewBox="0 0 180 38"><polyline id="avgSpark" points="0,31 20,27 40,29 60,21 80,25 100,15 120,21 140,12 160,18 180,8"/></svg></div>
  <div class="stat panel"><span>VALID SHARES</span><strong id="validShares">0</strong><small id="validPct">0.0%</small></div>
  <div class="stat panel"><span>INVALID SHARES</span><strong class="red" id="invalidShares">0</strong><small id="invalidPct">0.0%</small></div>
</div>
<div class="stats-row stats-balance">
  <div class="balance-stat confirmed"><span>CONFIRMED BALANCE</span><strong id="confirmedBalance">0 FIX</strong><small>confirmed / trusted</small></div>
  <div class="balance-stat pending"><span>UNCONFIRMED BALANCE</span><strong id="unconfirmedBalance">0 FIX</strong><small>follows immature balance</small></div>
  <div class="balance-stat immature"><span>IMMATURE BALANCE</span><strong id="immatureBalance">0 FIX</strong><small>coinbase maturity</small></div>
  <div class="balance-stat total"><span>TOTAL BALANCE</span><strong id="totalBalance">0 FIX</strong><small>follows confirmed balance</small></div>
  <div class="balance-stat eta"><span>EST. TIME TO BLOCK</span><strong id="eta">—</strong><small>(At current rate)</small></div>
</div>
</section>'''

stats_start = html.find('<section class="stats-grid">')
if stats_start < 0:
    raise RuntimeError('reference rebuild: stats-grid section not found')
stats_end = html.find('</section>', stats_start)
if stats_end < 0:
    raise RuntimeError('reference rebuild: stats-grid closing tag not found')
stats_end += len('</section>')
html = html[:stats_start] + stats + html[stats_end:]

HTML.write_text(html)
print('dashboard reference rebuild applied: structural forge/candidate normalization + explicit 3/5 metric rows')
