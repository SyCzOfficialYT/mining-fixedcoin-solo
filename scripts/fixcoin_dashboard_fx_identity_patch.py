#!/usr/bin/env python3
"""Install the second-generation geometric FX dashboard identity.

Idempotent build-time patch: replaces the old F/bolt mark, aligns the
candidate mark with the forge mark, and enables the richer Motion particle
layer plus the mythic Candidate/Treasury visual layer.
"""
from pathlib import Path
import re

HTML=Path('/app/monitor/templates/dashboard_v4.html')
html=HTML.read_text()

svg=r'''<svg class="fix-core-mark" viewBox="0 0 160 160" role="img" aria-label="FixedCoin FX core">
  <circle class="fix-core-ring r1" cx="80" cy="80" r="72"></circle>
  <circle class="fix-core-ring r2" cx="80" cy="80" r="62"></circle>
  <circle class="fix-core-ring r3" cx="80" cy="80" r="51"></circle>
  <polygon class="fix-core-shell" points="80,24 129,52 129,108 80,136 31,108 31,52"></polygon>
  <polygon class="fix-core-inner" points="80,39 114,59 114,101 80,121 46,101 46,59"></polygon>
  <path class="fix-core-glyph" d="M51 54 79 80 51 106 63 106 86 85 103 101 111 93 92 76 108 60 100 52 84 68 63 54Z"></path>
  <path class="fix-core-glyph-secondary" d="M55 80 68 67M92 93 105 80M55 80 68 93M92 67 105 80"></path>
  <circle class="fix-core-node" cx="80" cy="80" r="3.2"></circle>
  <path class="fix-core-scanline" d="M52 80h16M92 80h16"></path>
</svg>'''

m=re.search(r'<svg class="fix-core-mark"[\s\S]*?</svg>',html)
if not m:
    raise RuntimeError('FX identity patch: existing core SVG missing')
html=html[:m.start()]+svg+html[m.end():]

old='<div class="candidate-cube"><span>F</span></div>'
new='<div class="candidate-cube"><span class="candidate-glyph">FX</span></div>'
if old in html:
    html=html.replace(old,new,1)
elif 'class="candidate-glyph"' not in html:
    raise RuntimeError('FX identity patch: candidate logo anchor missing')

css_link='<link rel="stylesheet" href="/static/dashboard_v4_logo_fx.css?v=20260826-fx1">'
if 'dashboard_v4_logo_fx.css' not in html:
    html=html.replace('</head>',css_link+'\n</head>',1)
else:
    html=re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_logo_fx\.css\?v=[^"\s>]+">',css_link,html)

mythic_css='<link rel="stylesheet" href="/static/dashboard_v4_mythic_liveshare.css?v=20260826-mythic3">'
if 'dashboard_v4_mythic_liveshare.css' not in html:
    html=html.replace('</head>',mythic_css+'\n</head>',1)
else:
    html=re.sub(r'<link rel="stylesheet" href="/static/dashboard_v4_mythic_liveshare\.css\?v=[^"\s>]+">',mythic_css,html)

js_link='<script type="module" src="/static/dashboard_v4_logo_fx.js?v=20260826-fx1"></script>'
if 'dashboard_v4_logo_fx.js' not in html:
    html=html.replace('</body>',js_link+'\n</body>',1)

magic_old=r'<script type="module" src="/static/dashboard_v4_magic_particles\.js\?v=[^"\s>]+"></script>'
magic_new='<script type="module" src="/static/dashboard_v4_magic_particles_v2.js?v=20260826-magic2"></script>'
if re.search(magic_old,html):
    html=re.sub(magic_old,magic_new,html)
elif 'dashboard_v4_magic_particles_v2.js' not in html:
    html=html.replace('</body>',magic_new+'\n</body>',1)

mythic_js='<script type="module" src="/static/dashboard_v4_mythic_liveshare.js?v=20260826-mythic3"></script>'
if 'dashboard_v4_mythic_liveshare.js' not in html:
    html=html.replace('</body>',mythic_js+'\n</body>',1)

HTML.write_text(html)
print('dashboard FX identity patch applied: geometric FX core, matching candidate mark, enhanced Motion particles, mythic Candidate/Treasury layer')
