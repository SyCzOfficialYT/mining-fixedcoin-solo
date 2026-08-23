#!/usr/bin/env python3
from pathlib import Path

APP = Path('/app/monitor/app.py')
text = APP.read_text()
changed = False

def replace_once(old, new, label, required=True):
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

replace_once(
    'render_template("dashboard_v3.html",payout=config().get("payout_address",""),maturity=MATURITY)',
    'render_template("dashboard_v4.html",payout=config().get("payout_address",""),maturity=MATURITY)',
    'patched dashboard route: dashboard_v4.html',
    required=False,
)

replace_once(
    'BLOCKS = DATA / "blocks.json"\n',
    'BLOCKS = DATA / "blocks.json"\nLEDGER = Path(os.getenv("BLOCK_LEDGER_PATH", str(DATADIR / "solo-blocks.json")))\n',
    'patched dashboard block ledger path',
    required=False,
)
replace_once(
    'def read_ledger():\n    try:\n        rows=json.loads(BLOCKS.read_text()) if BLOCKS.exists() else []\n        return rows if isinstance(rows,list) else []\n    except Exception:\n        return []\n',
    '''def read_ledger():
    try:
        source = LEDGER if LEDGER.exists() else BLOCKS
        rows=json.loads(source.read_text()) if source.exists() else []
        return rows if isinstance(rows,list) else []
    except Exception:
        return []
''',
    'patched dashboard ledger reader',
    required=False,
)

replace_once(
    'if m: job["height"]=int(m.group(1)); job["network_diff"]=float(m.group(2))',
    'if m: job["height"]=int(m.group(1)); job["network_diff"]=float(m.group(2)); job["round_started_at"]=line[:19]',
    'patched dashboard round timestamp telemetry',
    required=False,
)
replace_once(
    '"started_at":stats.get("round_started_at"),"target_seconds":ROUND_SECONDS',
    '"started_at":stats.get("round_started_at") or log_job.get("round_started_at"),"target_seconds":ROUND_SECONDS',
    'patched dashboard timer source',
    required=False,
)
replace_once(
    'rejected=int(stats.get("shares_bad") or log_rejected or 0); accepted=int(stats.get("shares_ok") or len(shares));',
    'rejected=max(int(stats.get("shares_bad") or 0),int(log_rejected or 0)); accepted=max(int(stats.get("shares_ok") or 0),int(len(shares)),int(log_job.get("accepted") or 0));',
    'patched dashboard live share counters',
    required=False,
)
replace_once(
    'return accepted[-200:],rejected,blocks[-100:],workers,job',
    'job["accepted"]=len(accepted); return accepted[-200:],rejected,blocks[-100:],workers,job',
    'patched dashboard parsed share count',
    required=False,
)

if 'FIX_DASH_APP_STARTED' not in text:
    marker='WORKER_ACTIVE_SECONDS = int(os.getenv("WORKER_ACTIVE_SECONDS", "180"))\n'
    if marker in text:
        text=text.replace(marker,marker+'FIX_DASH_APP_STARTED = time.time()\n',1); changed=True
        print('patched dashboard app uptime marker')

if '"uptime_seconds"' not in text:
    needle='"ts":int(time.time())}'
    replacement='"ts":int(time.time()),"uptime_seconds":int(time.time()-FIX_DASH_APP_STARTED)}'
    if needle in text:
        text=text.replace(needle,replacement,1); changed=True
        print('patched dashboard status uptime field')

if changed:
    APP.write_text(text)
print('dashboard v4 backend repair complete')
