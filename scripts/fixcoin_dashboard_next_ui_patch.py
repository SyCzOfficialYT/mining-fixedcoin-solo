#!/usr/bin/env python3
from pathlib import Path

APP = Path("/app/monitor/app.py")
text = APP.read_text(encoding="utf-8")
old = 'def index(): return render_template("dashboard_liveshare.html",payout=config().get("payout_address",""),maturity=MATURITY)'
new = 'def index(): return app.send_static_file("next-ui/index.html")'

if old in text:
    text = text.replace(old, new, 1)
elif 'def index(): return app.send_static_file("next-ui/index.html")' in text:
    pass
else:
    raise SystemExit("dashboard root handler not found; refusing to patch")

APP.write_text(text, encoding="utf-8")
compile(text, str(APP), "exec")
print("dashboard root now serves Next.js LiveShare UI")
