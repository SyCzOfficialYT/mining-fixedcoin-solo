#!/usr/bin/env python3
"""Select the canonical LiveShare dashboard entrypoint.

The repository contains several historical dashboard compositions.  The v4 route
patch previously forced the compact dashboard_v4.html composition, which is not the
canonical LiveShare / Arcane reference layout.  The actual reference implementation
lives in dashboard_liveshare.html and receives its final rail/history/mobile visual
layer from the later Liveshare patches in the Docker build.

This patch changes only Flask's root template selection. API/telemetry logic remains
untouched. It is deliberately idempotent so rebuilds stay deterministic.
"""
from pathlib import Path
import re

APP = Path('/app/monitor/app.py')
s = APP.read_text(encoding='utf-8')

# Accept the historical v3/v4 route produced by earlier builds and converge it on
# the canonical LiveShare reference template. If the route is already correct,
# leave it untouched.
pattern = r'(@app\.get\("/"\)\s*\ndef index\(\):\s*)return render_template\("dashboard_(?:v3|v4|liveshare)\.html"'
replacement = r'\1return render_template("dashboard_liveshare.html"'
s2, n = re.subn(pattern, replacement, s, count=1)

if n == 1:
    APP.write_text(s2, encoding='utf-8')
    print('dashboard route patch applied: / now serves dashboard_liveshare.html')
elif 'return render_template("dashboard_liveshare.html"' in s:
    print('dashboard route patch already applied: / serves dashboard_liveshare.html')
else:
    raise RuntimeError('dashboard route patch: root dashboard route not found')
