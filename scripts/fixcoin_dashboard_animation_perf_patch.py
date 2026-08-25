#!/usr/bin/env python3
from pathlib import Path

HTML=Path('/app/monitor/templates/dashboard_v4.html')
h=HTML.read_text()
css='<link rel="stylesheet" href="/static/dashboard_v4_animation_perf.css?v=20260825-1">'
js='<script defer src="/static/dashboard_v4_animation_perf.js?v=20260825-1"></script>'

if 'dashboard_v4_animation_perf.css' not in h:
    p=h.find('</head>')
    if p<0: raise RuntimeError('animation perf: </head> missing')
    h=h[:p]+css+h[p:]
if 'dashboard_v4_animation_perf.js' not in h:
    p=h.rfind('</body>')
    if p<0: raise RuntimeError('animation perf: </body> missing')
    h=h[:p]+js+h[p:]

HTML.write_text(h)
print('dashboard animation perf applied: single canvas compositor + visibility pause + candidate particle canvas')
