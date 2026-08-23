#!/usr/bin/env python3
"""Apply the final FIXCOIN forge/proximity visual layer after all base dashboard patches."""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()

VERSION = '20260823-4'
CSS = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_upgrade.css?v={VERSION}">'
REF_CSS = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_reference.css?v={VERSION}">'
JS = f'<script defer src="/static/dashboard_v4_forge_upgrade.js?v={VERSION}"></script>'

# Inject exactly once. The scripts intentionally run late so they observe the
# authoritative dashboard_v4 realtime client instead of opening another API/SSE flow.
html = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_forge_upgrade\.css\?v=[^"]+">', '', html)
html = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_forge_reference\.css\?v=[^"]+">', '', html)
html = re.sub(r'<script[^>]+dashboard_v4_forge_upgrade\.js\?v=[^>]+></script>', '', html)

anchor = '<link rel="stylesheet" href="/static/dashboard_v4_forge_metrics_layout.css?v=20260823-1">'
if anchor not in html:
    raise RuntimeError('dashboard forge metrics stylesheet anchor missing')
html = html.replace(anchor, anchor + CSS + REF_CSS, 1)

anchor_js = '<script defer src="/static/dashboard_v4_share_parallax.js?v=20260823-9"></script>'
if anchor_js not in html:
    raise RuntimeError('dashboard forge client anchor missing')
html = html.replace(anchor_js, anchor_js + JS, 1)

# --- Compose the reference layout -------------------------------------------------
# The reference is one continuous Forge instrument: the Network Proximity HUD
# lives INSIDE the Forge outer panel, beneath the live proof-of-work stage.
# Existing IDs remain untouched so the realtime JS remains authoritative.
candidate_match = re.search(r'<section class="candidate panel" id="candidate">.*?</section>', html, flags=re.S)
if not candidate_match:
    raise RuntimeError('dashboard candidate section missing before forge integration')

candidate_html = candidate_match.group(0)
# Remove the standalone candidate section first.
html = html[:candidate_match.start()] + html[candidate_match.end():]

# Combo is kept as the left-gutter HUD element and moved into the Forge panel.
combo_match = re.search(r'<div class="combo" id="combo">.*?</div>', html, flags=re.S)
combo_html = combo_match.group(0) if combo_match else ''
if combo_match:
    html = html[:combo_match.start()] + html[combo_match.end():]

forge_start = html.find('<section class="forge panel" id="forge">')
if forge_start < 0:
    raise RuntimeError('dashboard forge section missing after candidate extraction')
forge_end = html.find('</section>', forge_start)
if forge_end < 0:
    raise RuntimeError('dashboard forge closing section missing')

html = html[:forge_end] + combo_html + candidate_html + html[forge_end:]

required = [
    'class="forge panel"',
    'id="forgeStage"',
    'id="forgeCore"',
    'id="candidate"',
    'id="candidatePct"',
    'class="candidate-track"',
    'id="combo"',
    'dashboard_v4_forge_upgrade.css',
    'dashboard_v4_forge_reference.css',
    'dashboard_v4_forge_upgrade.js',
]
missing = [x for x in required if x not in html]
if missing:
    raise RuntimeError('dashboard forge upgrade verification failed: ' + ', '.join(missing))

# Confirm the candidate section occurs after the Forge opening and before the
# outer Forge close. Because the candidate is itself a <section>, locate its
# own closing tag first and then require the next section close to be the Forge.
forge_start = html.find('<section class="forge panel" id="forge">')
candidate_pos = html.find('<section class="candidate panel" id="candidate">', forge_start)
if candidate_pos < 0:
    raise RuntimeError('dashboard forge upgrade verification failed: candidate not nested in forge')
candidate_end = html.find('</section>', candidate_pos)
forge_close = html.find('</section>', candidate_end + len('</section>'))
if not (forge_start < candidate_pos < candidate_end < forge_close):
    raise RuntimeError('dashboard forge upgrade verification failed: candidate is not inside forge outer section')

HTML.write_text(html)
print('dashboard forge upgrade applied: seamless Forge background, no Candidate card box, integrated Network Proximity HUD, persistent 0.001% progress particles, and block-found choreography')
