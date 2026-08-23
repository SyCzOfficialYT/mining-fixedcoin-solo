#!/usr/bin/env python3
"""Make the live balance/activity client the sole Recent Activity renderer."""
from pathlib import Path

JS = Path('/app/monitor/static/dashboard_v4.js')
text = JS.read_text()

anchor = "function renderActivity(){const host=$('activityList');"
replacement = "function renderActivity(){if(window.__FIXEDCOIN_DASH_BALANCE_ACTIVITY__)return;const host=$('activityList');"

if replacement not in text:
    if anchor not in text:
        raise RuntimeError('missing dashboard activity renderer anchor')
    text = text.replace(anchor, replacement, 1)
    JS.write_text(text)
    print('patched dashboard activity renderer authority: live activity client owns Recent Activity')
else:
    print('dashboard activity renderer authority already patched')

print('dashboard activity authority repair complete')
