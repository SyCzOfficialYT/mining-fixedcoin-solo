#!/usr/bin/env python3
"""Install/validate the repository-owned final dashboard reference composition."""
from pathlib import Path
import re

HTML=Path('/app/monitor/templates/dashboard_v4.html')
CSS=Path('/app/monitor/static/dashboard_v4_reference_final.css')
JS=Path('/app/monitor/static/dashboard_v4_reference_final.js')
RTCSS=Path('/app/monitor/static/dashboard_v4_reference_realtime.css')
html=HTML.read_text(); css=CSS.read_text(); js=JS.read_text(); rtcss=RTCSS.read_text()
rt_link='<link rel="stylesheet" href="/static/dashboard_v4_reference_realtime.css?v=20260825-1">'
html=re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_reference_realtime\.css\?v=[^"\s>]+">','',html)
head=html.find('</head>')
if head<0: raise RuntimeError('dashboard reference final: </head> missing')
html=html[:head]+rt_link+html[head:]
required_html=['class="reference-dashboard"','id="forgeStage"','id="forgeCore"','id="particleCanvas"','id="forgeParticles"','id="targetParticles"','id="candidateParticles"','id="liveVarDiff"','id="confirmedBalance"','id="unconfirmedBalance"','id="immatureBalance"','id="totalBalance"','id="candidateCore"','id="blockHistoryList"','dashboard_v4_reference_final.css','dashboard_v4_reference_final.js',rt_link]
missing=[x for x in required_html if x not in html]
required_css=['.reference-dashboard .forge-stage','.reference-dashboard .core-logo','.reference-dashboard .balance-grid','.bar-particles','.reference-dashboard .candidate-core']
missing += [x for x in required_css if x not in css]
required_js=['syncReferenceTelemetry','forgeParticles','makeBar','targetParticles','candidateParticles','pointerMove']
missing += [x for x in required_js if x not in js]
if 'core-hot' not in js or 'core-reject' not in js: missing.append('SSE core hit classes')
if 'rfCoreHit' not in rtcss or 'rfCoreReject' not in rtcss: missing.append('reference realtime core animations')
if missing: raise RuntimeError('dashboard reference final validation failed: '+', '.join(missing))
if '<img' in html or '<image' in html or 'dashboard_v4_miner.js' in html: raise RuntimeError('dashboard reference final: legacy raster/miner markup found')
ids=re.findall(r'id="([^"]+)"',html)
if len(ids)!=len(set(ids)): raise RuntimeError('dashboard reference final: duplicate HTML id detected')
HTML.write_text(html)
print('dashboard reference final verified: FIX HUD, 3D forge, SSE core-hit feedback, bar particles, balances, candidate HUD and canonical particle primitive')
