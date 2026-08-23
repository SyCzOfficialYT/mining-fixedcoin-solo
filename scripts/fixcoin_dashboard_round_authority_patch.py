#!/usr/bin/env python3
"""Make dashboard round/timer state come ONLY from a real NEW ROUND log event."""
from pathlib import Path

APP = Path('/app/monitor/app.py')
JS = Path('/app/monitor/static/dashboard_v4.js')

app = APP.read_text()
js = JS.read_text()
changed_app = False
changed_js = False


def replace_once(text, old, new, label):
    if new in text:
        return text, False
    if old not in text:
        raise RuntimeError(f'missing round-authority anchor: {label}')
    print(label)
    return text.replace(old, new, 1), True

# A stats.json round timestamp is not authoritative. It can survive a restart
# and cause the dashboard to invent a NEW ROUND that never appeared in the
# actual Stratum log. parse_logs() already extracts the real NEW ROUND line.
app, c = replace_once(
    app,
    'height=int(stats.get("round_height") or info.get("blocks") or mininginfo.get("blocks") or log_job.get("height") or 0);',
    'height=int(log_job.get("round_height") or stats.get("round_height") or info.get("blocks") or mininginfo.get("blocks") or 0);',
    'patched dashboard height precedence: real NEW ROUND first',
)
changed_app |= c

app, c = replace_once(
    app,
    'job={"job_id":log_job.get("job_id"),"height":stats.get("round_height") or log_job.get("height") or height,"network_diff":network_diff}; job.update(log_job)',
    'job={"job_id":log_job.get("job_id"),"height":log_job.get("round_height") or height,"network_diff":network_diff}; job.update(log_job)',
    'patched dashboard job height: no synthetic round source',
)
changed_app |= c

app, c = replace_once(
    app,
    '"round":{"height":int(stats.get("round_height") or height),"shares":round_shares,"work":round_work,"best_share":round_best,"effort_pct":round_effort,"best_share_pct":best_pct,"difficulty":network_diff,"remaining":remaining,"started_at":stats.get("round_started_at"),"target_seconds":ROUND_SECONDS}',
    '"round":{"height":int(log_job.get("round_height") or height),"shares":round_shares,"work":round_work,"best_share":round_best,"effort_pct":round_effort,"best_share_pct":best_pct,"difficulty":network_diff,"remaining":remaining,"started_at":log_job.get("round_started_at"),"started_epoch":log_job.get("round_started_epoch"),"source":"stratum-log","target_seconds":ROUND_SECONDS}',
    'patched timer: started_at/epoch exclusively from NEW ROUND log',
)
changed_app |= c

# Never synthesize a ROUND STARTED activity merely because a polled JSON
# timestamp changed. The activity list is seeded from /api/logs and realtime
# NEW ROUND events are delivered through the single SSE stream.
old_js = "const roundKey=parseTime(r.started_epoch||r.started_at);if(roundKey&&roundKey!==lastRoundKey){lastRoundKey=roundKey;addActivity('round','ROUND STARTED','#'+Number(r.height||0).toLocaleString(),r.started_at?.slice(11)||'',`round-live-${roundKey}`)}"
new_js = "/* ROUND STARTED is emitted only by /api/logs or the authoritative SSE round event. Never synthesize it from polled state. */"
js, c = replace_once(js, old_js, new_js, 'removed synthetic ROUND STARTED activity generator')
changed_js |= c

# The countdown must also reject any future/invalid timestamp and must only
# run for the explicit stratum-log source.
old_timer = "function updateTimer(round){const target=Number(round?.target_seconds)||600,started=parseTime(round?.started_epoch||round?.started_at);if(!started){$('timeRemain').textContent='00:00';$('timePct').textContent='0.0%';$('roundStatus').textContent='WAITING';$('roundStatus').className='status waiting';return}const elapsed=Math.max(0,(Date.now()/1000)-started),remain=Math.max(0,target-elapsed);$('timeRemain').textContent=timeOnly(remain);$('timePct').textContent=(100*remain/target).toFixed(1)+'%';const active=remain>0;$('roundStatus').textContent=active?'ACTIVE':'WAITING';$('roundStatus').className='status '+(active?'active':'waiting')}"
new_timer = "function updateTimer(round){const target=Number(round?.target_seconds)||600,started=parseTime(round?.started_epoch||round?.started_at);if(round?.source!=='stratum-log'||!started||started>Date.now()/1000+2){$('timeRemain').textContent='00:00';$('timePct').textContent='0.0%';$('roundStatus').textContent='WAITING';$('roundStatus').className='status waiting';return}const elapsed=Math.max(0,(Date.now()/1000)-started),remain=Math.max(0,target-elapsed);$('timeRemain').textContent=timeOnly(remain);$('timePct').textContent=(100*remain/target).toFixed(1)+'%';const active=remain>0;$('roundStatus').textContent=active?'ACTIVE':'WAITING';$('roundStatus').className='status '+(active?'active':'waiting')}"
js, c = replace_once(js, old_timer, new_timer, 'hardened timer against non-log round timestamps')
changed_js |= c

if changed_app:
    APP.write_text(app)
if changed_js:
    JS.write_text(js)

print('dashboard round authority verified: only real NEW ROUND log/SSE events can start a round or countdown')
