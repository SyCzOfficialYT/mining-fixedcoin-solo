#!/usr/bin/env python3
"""Final reference composition pass for dashboard v4.

Keeps the existing telemetry/IDs but rebuilds the visual composition around the supplied
reference: forge instruments, candidate card, explicit metric rows and separated balance cards.
"""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()

CSS = '<link rel="stylesheet" href="/static/dashboard_v4_reference_rebuild.css?v=20260825-1">'
html = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_reference_rebuild\.css\?v=[^"]+">', '', html)
html = html.replace('</head>', CSS + '</head>', 1)

# The reference has no activity list between candidate and the lower metrics.
html = re.sub(r'<div class="activity-panel">.*?</div></section>', '</section>', html, count=1, flags=re.S)

# IMPORTANT: the reference composition treats the Forge + Block Candidate as one
# physical instrument. Older patches left .combo inside .forge-stage and the
# .candidate section outside .forge. That makes the reference CSS selectors
# (.forge>.combo / .forge>.candidate) miss completely and produces the broken
# mobile geometry seen on the dashboard. Normalize the DOM here, after all
# earlier forge patches have finished touching the template.
combo_match = re.search(r'<div class="combo" id="combo">.*?</div>', html, flags=re.S)
candidate_match = re.search(
    r'<section class="candidate panel" id="candidate">.*?</section>(?=<section class="stats-grid">)',
    html,
    flags=re.S,
)
if not combo_match:
    raise RuntimeError('reference rebuild: combo markup not found')
if not candidate_match:
    raise RuntimeError('reference rebuild: candidate section not found')

combo = combo_match.group(0)
candidate = candidate_match.group(0)
html = html.replace(combo, '', 1)
html = html.replace(candidate, '', 1)

# The forge currently ends immediately before the old candidate section. Put the
# combo and candidate back at the forge level so the reference layout owns them.
forge_boundary = '</div></section><section class="stats-grid">'
if forge_boundary not in html:
    raise RuntimeError('reference rebuild: forge/stats boundary not found')
html = html.replace(
    forge_boundary,
    '</div>' + combo + candidate + '</section><section class="stats-grid">',
    1,
)

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

html, count = re.subn(r'<section class="stats-grid">.*?</section>', stats, html, count=1, flags=re.S)
if count != 1:
    raise RuntimeError('reference rebuild: stats-grid section not found')

HTML.write_text(html)
print('dashboard reference rebuild applied: forge + candidate DOM normalized, explicit forge/candidate composition + 3/5 metric rows')
