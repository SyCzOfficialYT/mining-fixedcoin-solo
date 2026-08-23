#!/usr/bin/env python3
"""Apply the final FIXCOIN forge/proximity visual layer."""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
html = HTML.read_text()
VERSION = '20260823-7'
REF = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_reference.css?v={VERSION}">'
UP = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_upgrade.css?v={VERSION}">'
TRAN = f'<link rel="stylesheet" href="/static/dashboard_v4_forge_transparency.css?v={VERSION}">'
JS = f'<script defer src="/static/dashboard_v4_forge_upgrade.js?v={VERSION}"></script>'
for pattern in (
    r'<link rel="stylesheet" href="/static/dashboard_v4_forge_reference\.css\?v=[^"]+">',
    r'<link rel="stylesheet" href="/static/dashboard_v4_forge_upgrade\.css\?v=[^"]+">',
    r'<link rel="stylesheet" href="/static/dashboard_v4_forge_transparency\.css\?v=[^"]+">',
    r'<script[^>]+dashboard_v4_forge_upgrade\.js\?v=[^>]+></script>',
):
    html = re.sub(pattern, '', html)
anchor = '<link rel="stylesheet" href="/static/dashboard_v4_forge_metrics_layout.css?v=20260823-1">'
if anchor not in html: raise RuntimeError('dashboard forge metrics stylesheet anchor missing')
html = html.replace(anchor, anchor + REF + UP + TRAN, 1)
anchor_js = '<script defer src="/static/dashboard_v4_share_parallax.js?v=20260823-9"></script>'
if anchor_js not in html: raise RuntimeError('dashboard forge client anchor missing')
html = html.replace(anchor_js, anchor_js + JS, 1)
candidate_match = re.search(r'<section class="candidate panel" id="candidate">.*?</section>', html, re.S)
if not candidate_match: raise RuntimeError('dashboard candidate section missing before forge integration')
candidate_html = candidate_match.group(0)
html = html[:candidate_match.start()] + html[candidate_match.end():]
combo_match = re.search(r'<div class="combo" id="combo">.*?</div>', html, re.S)
combo_html = combo_match.group(0) if combo_match else ''
if combo_match: html = html[:combo_match.start()] + html[combo_match.end():]
forge_start = html.find('<section class="forge panel" id="forge">')
if forge_start < 0: raise RuntimeError('dashboard forge section missing after candidate extraction')
forge_end = html.find('</section>', forge_start)
html = html[:forge_end] + combo_html + candidate_html + html[forge_end:]
required = ['class="forge panel"','id="forgeStage"','id="forgeCore"','id="candidate"','id="candidatePct"','class="candidate-track"','id="combo"','dashboard_v4_forge_reference.css','dashboard_v4_forge_upgrade.css','dashboard_v4_forge_transparency.css','dashboard_v4_forge_upgrade.js']
missing = [x for x in required if x not in html]
if missing: raise RuntimeError('dashboard forge upgrade verification failed: ' + ', '.join(missing))
forge_start = html.find('<section class="forge panel" id="forge">')
candidate_pos = html.find('<section class="candidate panel" id="candidate">', forge_start)
candidate_end = html.find('</section>', candidate_pos)
forge_close = html.find('</section>', candidate_end + len('</section>'))
if not (forge_start < candidate_pos < candidate_end < forge_close): raise RuntimeError('dashboard forge upgrade verification failed: candidate is not inside forge outer section')
HTML.write_text(html)
print('dashboard forge upgrade applied: fully transparent candidate HUD with inherited Forge atmosphere and unclipped Forge artwork')
