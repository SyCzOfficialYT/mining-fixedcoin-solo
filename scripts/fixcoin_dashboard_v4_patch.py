#!/usr/bin/env python3
"""Harden the v4 dashboard backend for realtime round state and block validity."""
from pathlib import Path
import re

APP = Path('/app/monitor/app.py')
text = APP.read_text()
changed = False

def once(old, new, label, required=False):
    global text, changed
    if new in text:
        return
    if old not in text:
        if required:
            raise RuntimeError(label)
        return
    text = text.replace(old, new, 1)
    changed = True
    print(label)

# v4 route
once(
    'render_template("dashboard_v3.html",payout=config().get("payout_address",""),maturity=MATURITY)',
    'render_template("dashboard_v4.html",payout=config().get("payout_address",""),maturity=MATURITY)',
    'patched dashboard route: dashboard_v4.html',
)

# Persistent block ledger: prefer the dedicated solo ledger, then legacy blocks.json.
once(
    'BLOCKS = DATA / "blocks.json"\n',
    'BLOCKS = DATA / "blocks.json"\nLEDGER = Path(os.getenv("BLOCK_LEDGER_PATH", str(DATADIR / "solo-blocks.json")))\n',
    'patched dashboard block ledger path',
)
once(
'''def read_ledger():
    try:
        rows=json.loads(BLOCKS.read_text()) if BLOCKS.exists() else []
        return rows if isinstance(rows,list) else []
    except Exception:
        return []
''',
'''def read_ledger():
    try:
        source = LEDGER if LEDGER.exists() else BLOCKS
        rows=json.loads(source.read_text()) if source.exists() else []
        return rows if isinstance(rows,list) else []
    except Exception:
        return []
''',
    'patched dashboard ledger reader',
)

# Capture the actual NEW ROUND log timestamp. This is the authoritative local
# start time for the 10-minute round timer; it survives page reloads.
if 'job["round_started_at"]=' not in text:
    pattern = r'(m=re\.search\(r"NEW ROUND\\s\+height=\(\\d\+\)\\s\+netdiff=\(\[0-9\.eE\+\-\]\+\)",line,re\.I\)\n\s*if m: job\["height"\]=int\(m\.group\(1\)\); job\["network_diff"\]=float\(m\.group\(2\)\))'
    replacement = r'\1; job["round_started_at"]=line[:19]'
    new_text, n = re.subn(pattern, replacement, text, count=1)
    if n:
        text = new_text
        changed = True
        print('patched dashboard round timestamp telemetry')
    else:
        # Fallback for formatting variants: inject immediately after the
        # NEW ROUND height/network assignment line.
        marker = 'job["height"]=int(m.group(1)); job["network_diff"]=float(m.group(2))'
        if marker in text:
            text = text.replace(marker, marker + '; job["round_started_at"]=line[:19]', 1)
            changed = True
            print('patched dashboard round timestamp telemetry (fallback)')

# Expose the timestamp through /api/status.
old = '"started_at":stats.get("round_started_at"),"target_seconds":ROUND_SECONDS'
new = '"started_at":stats.get("round_started_at") or log_job.get("round_started_at"),"target_seconds":ROUND_SECONDS'
once(old, new, 'patched dashboard timer source')

# Keep counters monotonic when stats.json lags the live log parser.
once(
    'rejected=int(stats.get("shares_bad") or log_rejected or 0); accepted=int(stats.get("shares_ok") or len(shares));',
    'rejected=max(int(stats.get("shares_bad") or 0),int(log_rejected or 0)); accepted=max(int(stats.get("shares_ok") or 0),int(len(shares)),int(log_job.get("accepted") or 0));',
    'patched dashboard live share counters',
)
once(
    'return accepted[-200:],rejected,blocks[-100:],workers,job',
    'job["accepted"]=len(accepted); job["rejected"]=rejected; return accepted[-200:],rejected,blocks[-100:],workers,job',
    'patched dashboard parsed share counts',
)

# Dashboard process uptime.
if 'FIX_DASH_APP_STARTED' not in text:
    marker = 'WORKER_ACTIVE_SECONDS = int(os.getenv("WORKER_ACTIVE_SECONDS", "180"))\n'
    if marker in text:
        text = text.replace(marker, marker + 'FIX_DASH_APP_STARTED = time.time()\n', 1)
        changed = True
        print('patched dashboard app uptime marker')
if '"uptime_seconds"' not in text:
    needle = '"ts":int(time.time())}'
    if needle in text:
        text = text.replace(needle, '"ts":int(time.time()),"uptime_seconds":int(time.time()-FIX_DASH_APP_STARTED)}', 1)
        changed = True
        print('patched dashboard status uptime field')

if changed:
    APP.write_text(text)
print('dashboard v4 backend repair complete')
