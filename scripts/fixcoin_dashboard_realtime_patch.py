#!/usr/bin/env python3
from pathlib import Path

APP = Path('/app/monitor/app.py')
HTML = Path('/app/monitor/templates/dashboard_v3.html')
MARKER = '@app.get("/")\n'
IMPORT_OLD = 'from flask import Flask, jsonify, render_template\n'
IMPORT_NEW = 'from flask import Flask, Response, jsonify, render_template\n'

INSERT = r'''\
@app.get("/api/stream")
def api_stream():
    """Low-latency SSE stream for live Stratum share/block telemetry."""
    def generate():
        import json as _json
        import re as _re
        import time as _time
        path = LOG
        offset = 0
        inode = None
        last_heartbeat = _time.time()
        while True:
            try:
                st = path.stat()
                if inode != st.st_ino or st.st_size < offset:
                    inode = st.st_ino
                    offset = 0
                with path.open('r', errors='replace') as fh:
                    fh.seek(offset)
                    data = fh.read()
                    offset = fh.tell()
                for line in data.splitlines():
                    payload = None
                    ts = line[:19]
                    m = _re.search(r'ACCEPT\s+#(\d+)\s+work=([0-9.]+).*?(?:pool|pool_diff)=([0-9.]+).*?hash=([0-9a-fA-F]+)', line, _re.I)
                    if m:
                        num, work, diff, h = m.groups()
                        payload = {'type':'accept','ts':ts,'num':int(num),'work':float(work),'pool_diff':float(diff),'hash':h}
                    else:
                        m = _re.search(r'REJECT\s+reason=([^\s]+).*?share_diff=([0-9.]+).*?(?:required_diff|current_diff)=([0-9.]+).*?hash=([0-9a-fA-F]+)', line, _re.I)
                        if m:
                            reason, share_diff, required, h = m.groups()
                            payload = {'type':'reject','ts':ts,'reason':reason,'share_diff':float(share_diff),'required_diff':float(required),'hash':h}
                        elif 'NEW ROUND' in line:
                            m = _re.search(r'NEW ROUND\s+height=(\d+)\s+netdiff=([0-9.eE+-]+)', line, _re.I)
                            if m:
                                payload = {'type':'round','ts':ts,'height':int(m.group(1)),'network_diff':float(m.group(2))}
                        elif _re.search(r'\bBLOCK\b|BLOCK FOUND|FOUND BLOCK', line, _re.I):
                            payload = {'type':'block','ts':ts,'message':line[20:].strip() if len(line)>20 else line}
                    if payload:
                        yield 'data: ' + _json.dumps(payload, separators=(',', ':')) + '\n\n'
                now = _time.time()
                if now - last_heartbeat >= 10:
                    yield ': heartbeat\n\n'
                    last_heartbeat = now
                _time.sleep(0.10)
            except GeneratorExit:
                return
            except Exception as exc:
                yield 'data: ' + _json.dumps({'type':'stream_error','error':str(exc)}) + '\n\n'
                _time.sleep(1)
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control':'no-cache, no-store, must-revalidate',
        'X-Accel-Buffering':'no',
        'Connection':'keep-alive',
    })

'''.lstrip('\\')

text = APP.read_text()
if 'def api_stream()' not in text:
    if IMPORT_OLD not in text:
        raise RuntimeError('Flask import line not found')
    if MARKER not in text:
        raise RuntimeError('dashboard route marker not found')
    text = text.replace(IMPORT_OLD, IMPORT_NEW, 1)
    text = text.replace(MARKER, INSERT + MARKER, 1)
    APP.write_text(text)
    print('patched dashboard app: /api/stream SSE')
else:
    print('dashboard realtime stream already present')

# Bump the dashboard loader URL so browsers cannot keep an older cached effects loader.
if HTML.exists():
    html = HTML.read_text()
    old = '/static/dashboard_effects.js?v=2026-08-23-miner-flow-1'
    new = '/static/dashboard_effects.js?v=2026-08-23-miner-flow-2'
    if old in html:
        html = html.replace(old, new, 1)
        HTML.write_text(html)
        print('bumped dashboard effects cache version')
    elif 'dashboard_effects.js?v=2026-08-23-miner-flow-2' in html:
        print('dashboard effects cache version already current')
    else:
        raise RuntimeError('dashboard effects loader marker not found')
