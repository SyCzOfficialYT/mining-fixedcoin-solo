#!/usr/bin/env python3
"""Install the final dashboard visual layer after every other v4 stylesheet.

No telemetry or mining logic is changed here. The layer only strengthens the
FIXCORE HUD, candidate particle presentation, and mobile composition.
"""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
h = HTML.read_text()

css = '<link rel="stylesheet" href="/static/dashboard_v4_visual_final.css?v=20260825-1">'
h = re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_visual_final\.css\?v=[^"\s>]+">', '', h)
pos = h.find('</head>')
if pos < 0:
    raise RuntimeError('visual final: </head> missing')
h = h[:pos] + css + h[pos:]

required = [
    'id="forgeStage"',
    'id="forgeCore"',
    'id="candidate"',
    'id="candidatePct"',
    'class="candidate-track"',
    'class="candidate-core"',
]
missing = [x for x in required if x not in h]
if missing:
    raise RuntimeError('visual final: missing primitives: ' + ', '.join(missing))

HTML.write_text(h)
print('dashboard visual final applied: FIXCORE HUD + candidate particle presentation + mobile visual correction')
