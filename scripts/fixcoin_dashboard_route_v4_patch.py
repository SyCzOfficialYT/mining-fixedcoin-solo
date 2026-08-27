#!/usr/bin/env python3
"""Select the canonical v4 reference dashboard entrypoint.

The final LiveShare/Arcane reference composition is owned by
``monitor/templates/dashboard_v4.html``.  Historical dashboard templates
remain in the repository for reference, but the root route must never select
them during a production build.

This patch changes only Flask's root template selection. API/telemetry logic
remains untouched. It is deliberately idempotent so rebuilds stay deterministic.
"""
from pathlib import Path
import re

APP = Path('/app/monitor/app.py')
s = APP.read_text(encoding='utf-8')

pattern = r'(@app\.get\("/"\)\s*\ndef index\(\):\s*)return render_template\("dashboard_(?:v2|v3|v4|liveshare)\.html"'
replacement = r'\1return render_template("dashboard_v4.html"'
s2, n = re.subn(pattern, replacement, s, count=1)

if n == 1:
    APP.write_text(s2, encoding='utf-8')
    print('dashboard route patch applied: / now serves dashboard_v4.html')
elif 'return render_template("dashboard_v4.html"' in s:
    print('dashboard route patch already applied: / serves dashboard_v4.html')
else:
    raise RuntimeError('dashboard route patch: root dashboard route not found')
