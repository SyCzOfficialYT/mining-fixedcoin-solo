#!/usr/bin/env python3
"""Validate the canonical v4 realtime backend and repository-owned reference HUD."""
from pathlib import Path
import re

JS=Path('/app/monitor/static/dashboard_v4.js')
HTML=Path('/app/monitor/templates/dashboard_v4.html')
FORGE_JS=Path('/app/monitor/static/dashboard_v4_forge.js')
FORGE_CSS=Path('/app/monitor/static/dashboard_v4_forge.css')
text=JS.read_text(); html=HTML.read_text(); forge_js=FORGE_JS.read_text(); forge_css=FORGE_CSS.read_text()
required=['function render(s,animate=false){','async function poll(animate=false){',"new EventSource('/api/stream')",'function burstParticles(','function strike(','started_epoch',"if(e.type==='accept')","if(e.type==='reject')",'particleCanvas','spawnParticle(']
missing=[item for item in required if item not in text]

# The reference dashboard uses multiple classes on the root element, e.g.
# <main class="dashboard reference-dashboard">. Validate the class token,
# rather than requiring the brittle exact string class="reference-dashboard".
if not re.search(r'class="[^"]*\breference-dashboard\b[^"]*"', html):
    missing.append('class token reference-dashboard')

html_any=[('id="forgeCore"','id="forgeCore"'),('forge-center','forge-center'),('id="forgeParticles"','id="forgeParticles"')]
for label,needle in html_any:
    if needle in html: break
else:
    missing.append('FIXCORE reference primitive (forgeCore/forge-center/forgeParticles)')
for needle in ('dashboard_v4_forge.css','id="acceptedCounter"','id="rejectedCounter"'):
    if needle not in html: missing.append(needle)
forge_required=['fixedcoin:accept','fixedcoin:reject','fixedcoin:block','hit-accept','hit-reject','hit-block']
missing += [item for item in forge_required if item not in forge_js]
css_required=['.forge-core{','.core-energy{','.forge-ring{','.forge.hit-accept','.forge.hit-reject']
missing += [item for item in css_required if item not in forge_css]
if 'particleCanvas' not in html and 'particleCanvas' not in text: missing.append('particleCanvas|realtime particle primitive')
if missing: raise RuntimeError('dashboard v4 realtime/FIXCORE validation failed: '+', '.join(missing))
for forbidden in ('miner_reference.svg','<img','<image','dashboard_v4_miner.js'):
    if forbidden in html: raise RuntimeError('legacy miner primitive found in dashboard template: '+forbidden)
print('dashboard v4 verified: realtime renderer, canonical particle primitive, reference FIX HUD, accept/reject/block motion and no legacy miner markup')
