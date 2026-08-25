#!/usr/bin/env python3
"""Validate the repository-owned final dashboard reference composition.

This is intentionally the last dashboard visual step in the image build. The
historical v4 visual patch chain is not run anymore because it was designed for
older DOM contracts and could overwrite the reference composition.
"""
from pathlib import Path
import re

HTML=Path('/app/monitor/templates/dashboard_v4.html')
CSS=Path('/app/monitor/static/dashboard_v4_reference_final.css')
JS=Path('/app/monitor/static/dashboard_v4_reference_final.js')
html=HTML.read_text(); css=CSS.read_text(); js=JS.read_text()
required_html=[
    'class="reference-dashboard"','id="forgeStage"','id="forgeCore"','id="particleCanvas"',
    'id="forgeParticles"','id="targetParticles"','id="candidateParticles"','id="liveVarDiff"',
    'id="confirmedBalance"','id="unconfirmedBalance"','id="immatureBalance"','id="totalBalance"',
    'id="candidateCore"','id="blockHistoryList"','dashboard_v4_reference_final.css','dashboard_v4_reference_final.js',
]
missing=[x for x in required_html if x not in html]
required_css=['.reference-dashboard .forge-stage','.reference-dashboard .core-logo','.reference-dashboard .balance-grid','.bar-particles','.reference-dashboard .candidate-core']
missing += [x for x in required_css if x not in css]
required_js=['syncReferenceTelemetry','forgeParticles','makeBar','targetParticles','candidateParticles','pointerMove']
missing += [x for x in required_js if x not in js]
if missing:
    raise RuntimeError('dashboard reference final validation failed: '+', '.join(missing))
if '<img' in html or '<image' in html or 'dashboard_v4_miner.js' in html:
    raise RuntimeError('dashboard reference final: legacy raster/miner markup found')
if len(re.findall(r'id="([^"]+)"',html)) != len(set(re.findall(r'id="([^"]+)"',html))):
    raise RuntimeError('dashboard reference final: duplicate HTML id detected')
print('dashboard reference final verified: FIX HUD, 3D forge, bar particles, balances, candidate HUD and canonical particle primitive')
