#!/usr/bin/env python3
"""Install/validate the repository-owned final dashboard reference composition."""
from pathlib import Path
import re

HTML=Path('/app/monitor/templates/dashboard_v4.html');CSS=Path('/app/monitor/static/dashboard_v4_reference_final.css');JS=Path('/app/monitor/static/dashboard_v4_reference_final.js');SHELL_JS=Path('/app/monitor/static/dashboard_v4_reference_shell.js');CORE_CSS=Path('/app/monitor/static/dashboard_v4_core_motion.css');CORE_JS=Path('/app/monitor/static/dashboard_v4_core_motion.js');RTCSS=Path('/app/monitor/static/dashboard_v4_reference_realtime.css')
html=HTML.read_text();css=CSS.read_text();js=JS.read_text();shell_js=SHELL_JS.read_text();core_css=CORE_CSS.read_text();core_js=CORE_JS.read_text();rtcss=RTCSS.read_text()
rt_link='<link rel="stylesheet" href="/static/dashboard_v4_reference_realtime.css?v=20260828-reference3">';shell_script='<script defer src="/static/dashboard_v4_reference_shell.js?v=20260828-reference3"></script>'
html=re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_reference_realtime\.css\?v=[^"\s>]+">','',html);html=re.sub(r'<script defer src="/static/dashboard_v4_reference_shell\.js\?v=[^"\s>]+"></script>','',html)
html=re.sub(r'/static/dashboard_v4_reference_alignment\.css\?v=[^"\s>]+','/static/dashboard_v4_reference_alignment.css?v=20260828-reference3',html)
head=html.find('</head>');body=html.find('</body>')
if head<0 or body<0:raise RuntimeError('dashboard reference final: document boundary missing')
html=html[:head]+rt_link+html[head:];body=html.find('</body>');html=html[:body]+shell_script+html[body:]
height_marker='const heightFmt=v=>{const n=Math.trunc(Number(v)||0);return n.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g,",")};'
if height_marker not in js:
    anchor='const $=id=>document.getElementById(id);'
    if anchor not in js:raise RuntimeError('dashboard reference final: JS height formatter anchor missing')
    js=js.replace(anchor,anchor+height_marker,1)
for old,new in {"Number(r.height||n.height||0).toLocaleString()":"heightFmt(r.height||n.height||0)","(Number(r.height||n.height||0)+1).toLocaleString()":"heightFmt(Number(r.height||n.height||0)+1)","Number(b.height||0).toLocaleString()":"heightFmt(b.height||0)","Number(round[1]).toLocaleString()":"heightFmt(round[1])","Number(r.height||0).toLocaleString()":"heightFmt(r.height||0)"}.items():js=js.replace(old,new)
HTML.write_text(html);JS.write_text(js)
required_html=['id="forgeStage"','id="forgeCore"','id="particleCanvas"','id="forgeParticles"','id="targetParticles"','id="candidateParticles"','id="liveVarDiff"','id="confirmedBalance"','id="unconfirmedBalance"','id="immatureBalance"','id="totalBalance"','id="candidateCore"','id="blockHistoryList"','dashboard_v4_reference_final.css','dashboard_v4_reference_final.js','dashboard_v4_reference_shell.js','dashboard_v4_reference_alignment.css?v=20260828-reference3','dashboard_v4_core_motion.css','dashboard_v4_core_motion.js',rt_link];missing=[x for x in required_html if x not in html]
if not re.search(r'class="[^"]*\breference-dashboard\b[^"]*"',html):missing.append('class token reference-dashboard')
required_css=['.reference-dashboard .forge-stage','.reference-dashboard .core-logo','.reference-dashboard .balance-grid','.bar-particles','.reference-dashboard .candidate-core'];missing += [x for x in required_css if x not in css]
required_js=['syncReferenceTelemetry','pointerMove','heightFmt','fixedcoin:live'];missing += [x for x in required_js if x not in js]
required_shell=['reference-nav','reference-rail','reference-balance-stack','railWorkers','IntersectionObserver'];missing += [x for x in required_shell if x not in shell_js]
required_core_css=['.fix-core-mark','.fix-core-ring','will-change:transform','prefers-reduced-motion'];missing += [x for x in required_core_css if x not in core_css]
required_core_js=['document.documentElement.dataset.fixedcoinCoreMotion','motion-active','fxCoreFloat','fxCoreHit','fxBlock','prefers-reduced-motion'];missing += [x for x in required_core_js if x not in core_js]
if 'motion@13.1.1/mini/+esm' in core_js:raise RuntimeError('dashboard reference final: unexpected external Motion CDN in local core')
if 'rfCoreHit' not in rtcss or 'rfCoreReject' not in rtcss:missing.append('reference realtime core animations')
if missing:raise RuntimeError('dashboard reference final validation failed: '+', '.join(missing))
if '<img' in html or '<image' in html or 'dashboard_v4_miner.js' in html:raise RuntimeError('dashboard reference final: legacy raster/miner markup found')
ids=re.findall(r'id="([^"]+)"',html)
if len(ids)!=len(set(ids)):raise RuntimeError('dashboard reference final: duplicate HTML id detected')
print('dashboard reference final verified: LiveShare reference shell, dynamic nav/rail, FIX HUD, local Arcane motion, event-driven feedback, mobile composition, balances, candidate HUD, particles, and locale-safe block heights')
