#!/usr/bin/env python3
"""Make the live dashboard route serve the fully patched v4 reference template.

The visual/reference patch chain operates on dashboard_v4.html, while the Flask root
route historically served dashboard_v3.html. That made the build succeed but left the
browser on the legacy composition. Keep the API/telemetry untouched and switch only the
HTML entrypoint.
"""
from pathlib import Path
import re

APP = Path('/app/monitor/app.py')
s = APP.read_text()

pattern = r'(@app\.get\("/"\)\s*\ndef index\(\):\s*)return render_template\("dashboard_v3\.html"'
replacement = r'\1return render_template("dashboard_v4.html"'
s2, n = re.subn(pattern, replacement, s, count=1)

if n != 1:
    raise RuntimeError('dashboard route patch: expected dashboard_v3.html root route not found')

APP.write_text(s2)
print('dashboard route patch applied: / now serves dashboard_v4.html')
