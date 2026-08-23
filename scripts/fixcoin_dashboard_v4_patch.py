#!/usr/bin/env python3
from pathlib import Path

APP = Path('/app/monitor/app.py')
text = APP.read_text()
changed = False

old = 'render_template("dashboard_v3.html",payout=config().get("payout_address",""),maturity=MATURITY)'
new = 'render_template("dashboard_v4.html",payout=config().get("payout_address",""),maturity=MATURITY)'
if 'render_template("dashboard_v4.html"' in text:
    print('dashboard v4 route already active')
elif old in text:
    text = text.replace(old, new, 1)
    changed = True
    print('patched dashboard route: dashboard_v4.html')
else:
    raise RuntimeError('dashboard render route not found')

if 'FIX_DASH_APP_STARTED' not in text:
    marker = 'WORKER_ACTIVE_SECONDS = int(os.getenv("WORKER_ACTIVE_SECONDS", "180"))\n'
    inject = marker + 'FIX_DASH_APP_STARTED = time.time()\n'
    if marker not in text:
        raise RuntimeError('dashboard uptime anchor not found')
    text = text.replace(marker, inject, 1)
    changed = True
    print('patched dashboard uptime telemetry')

if '@app.get("/api/stream")' not in text:
    marker = '@app.get("/api/logs")\n'
    stream = """
@app.get("/api/stream")
def api_stream():
    def generate():
        last_mtime = 0
        last_sig = None
        while True:
            try:
                mtime = LOG.stat().st_mtime_ns if LOG.exists() else 0
                if mtime != last_mtime:
                    recent = lines(LOG, 40)
                    event_type = "state"
                    for line in reversed(recent):
                        if "ACCEPT" in line:
                            event_type = "accept"; break
                        if "REJECT" in line or "low difficulty" in line.lower():
                            event_type = "reject"; break
                        if "NEW ROUND" in line:
                            event_type = "round"; break
                        if "BLOCK" in line:
                            event_type = "block"; break
                    sig = (mtime, event_type)
                    if sig != last_sig:
                        payload = json.dumps({'type': event_type, 'ts': int(time.time())})
                        yield "data: " + payload + chr(10) + chr(10)
                        last_sig = sig
                    last_mtime = mtime
                else:
                    yield ": heartbeat" + chr(10) + chr(10)
                time.sleep(0.5)
            except GeneratorExit:
                return
            except Exception:
                yield ": heartbeat" + chr(10) + chr(10)
                time.sleep(1)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )

"""
    if marker not in text:
        raise RuntimeError('dashboard log endpoint anchor not found')
    text = text.replace(marker, stream + marker, 1)
    changed = True
    print('patched dashboard realtime SSE endpoint')

if 'from flask import Flask, jsonify, render_template, Response' not in text:
    text = text.replace(
        'from flask import Flask, jsonify, render_template',
        'from flask import Flask, jsonify, render_template, Response',
        1,
    )
    changed = True
    print('patched dashboard Response import')

needle = '"ts":int(time.time())}'
replacement = '"ts":int(time.time()),"uptime_seconds":int(time.time()-FIX_DASH_APP_STARTED)}'
if '"uptime_seconds"' not in text:
    if needle not in text:
        raise RuntimeError('dashboard status return anchor not found')
    text = text.replace(needle, replacement, 1)
    changed = True
    print('patched dashboard status uptime field')

if changed:
    APP.write_text(text)
print('dashboard backend patch complete')
