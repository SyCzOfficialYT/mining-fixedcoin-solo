#!/usr/bin/env python3
from pathlib import Path

APP=Path('/app/monitor/app.py')
text=APP.read_text()
old='render_template("dashboard_v3.html",payout=config().get("payout_address",""),maturity=MATURITY)'
new='render_template("dashboard_v4.html",payout=config().get("payout_address",""),maturity=MATURITY)'
if 'render_template("dashboard_v4.html"' in text:
    print('dashboard v4 already active')
elif old in text:
    APP.write_text(text.replace(old,new,1))
    print('patched dashboard route: dashboard_v4.html')
else:
    raise RuntimeError('dashboard_v3 render route not found')
