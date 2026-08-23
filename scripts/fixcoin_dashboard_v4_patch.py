#!/usr/bin/env python3
"""Harden the v4 dashboard backend around authoritative Stratum round state."""
from pathlib import Path

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

once('render_template("dashboard_v3.html",payout=config().get("payout_address",""),maturity=MATURITY)',
     'render_template("dashboard_v4.html",payout=config().get("payout_address",""),maturity=MATURITY)',
     'patched dashboard route: dashboard_v4.html')

once('BLOCKS = DATA / "blocks.json"\n',
     'BLOCKS = DATA / "blocks.json"\nLEDGER = Path(os.getenv("BLOCK_LEDGER_PATH", str(DATADIR / "solo-blocks.json")))\n',
     'patched dashboard block ledger path')
once('''def read_ledger():
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
''', 'patched dashboard ledger reader')

# Only a real NEW ROUND log line starts a dashboard round. Job notifications do not.
once('accepted, rejected, blocks, workers, job = [], 0, [], {}, {}',
     'accepted, rejected, blocks, workers, job = [], 0, [], {}, {}\n    round_height=0; round_started_at=None; round_started_epoch=0',
     'patched authoritative round telemetry state')
once('''m=re.search(r"NEW ROUND\\s+height=(\\d+)\\s+netdiff=([0-9.eE+-]+)",line,re.I)
        if m: job["height"]=int(m.group(1)); job["network_diff"]=float(m.group(2))''',
'''m=re.search(r"NEW ROUND\\s+height=(\\d+)\\s+netdiff=([0-9.eE+-]+)",line,re.I)
        if m:
            round_height=int(m.group(1)); round_started_at=line[:19]; round_started_epoch=ts
            job["round_height"]=round_height; job["round_started_at"]=round_started_at; job["round_started_epoch"]=round_started_epoch; job["network_diff"]=float(m.group(2))''',
     'patched NEW ROUND as sole round-start source')
once('''m=re.search(r"Job\\s+([^\\s]+).*?height=(\\d+).*?(?:miner=([0-9.eE+-]+))?.*?(?:dev=([0-9.eE+-]+))?",line,re.I)
        if m:
            job.update({"job_id":m.group(1),"height":int(m.group(2))})''',
'''m=re.search(r"Job\\s+([^\\s]+).*?height=(\\d+).*?(?:miner=([0-9.eE+-]+))?.*?(?:dev=([0-9.eE+-]+))?",line,re.I)
        if m:
            job.update({"job_id":m.group(1),"job_height":int(m.group(2))})''',
     'patched Job telemetry so it cannot start rounds')
once('return accepted[-200:],rejected,blocks[-100:],workers,job',
     'job["round_height"]=round_height; job["round_started_at"]=round_started_at; job["round_started_epoch"]=round_started_epoch; return accepted[-200:],rejected,blocks[-100:],workers,job',
     'patched authoritative round return')

if 'FIX_DASH_APP_STARTED' not in text:
    marker='WORKER_ACTIVE_SECONDS = int(os.getenv("WORKER_ACTIVE_SECONDS", "180"))\n'
    if marker in text:
        text=text.replace(marker,marker+'FIX_DASH_APP_STARTED = time.time()\n',1); changed=True; print('patched dashboard app uptime marker')

once('rejected=int(stats.get("shares_bad") or log_rejected or 0); accepted=int(stats.get("shares_ok") or len(shares));',
     'rejected=max(int(stats.get("shares_bad") or 0),int(log_rejected or 0)); accepted=max(int(stats.get("shares_ok") or 0),int(len(shares)),int(log_job.get("accepted") or 0));',
     'patched dashboard live share counters')

once('job={"job_id":log_job.get("job_id"),"height":stats.get("round_height") or log_job.get("height") or height,"network_diff":network_diff}; job.update(log_job)',
     'job={"job_id":log_job.get("job_id"),"height":stats.get("round_height") or log_job.get("round_height") or height,"network_diff":network_diff}; job.update(log_job)',
     'patched dashboard authoritative job height')
once('"started_at":stats.get("round_started_at"),"target_seconds":ROUND_SECONDS',
     '"started_at":log_job.get("round_started_at") or stats.get("round_started_at"),"started_epoch":log_job.get("round_started_epoch") or stats.get("round_started_epoch"),"target_seconds":ROUND_SECONDS',
     'patched dashboard authoritative timer source')

if '"uptime_seconds"' not in text:
    needle='"ts":int(time.time())}'
    if needle in text:
        text=text.replace(needle,'"ts":int(time.time()),"uptime_seconds":int(time.time()-FIX_DASH_APP_STARTED)}',1); changed=True; print('patched dashboard status uptime field')

if changed:
    APP.write_text(text)
print('dashboard v4 backend repair complete')
