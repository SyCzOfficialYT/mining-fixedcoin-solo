#!/usr/bin/env python3
"""Make dashboard round/timer state come ONLY from a real NEW ROUND log event."""
from pathlib import Path

APP=Path('/app/monitor/app.py')
JS=Path('/app/monitor/static/dashboard_v4.js')
app=APP.read_text(); js=JS.read_text(); changed_app=False; changed_js=False

def any_replace(text, variants, new, label):
    if new in text:return text,False
    for old in variants:
        if old in text:
            print(label);return text.replace(old,new,1),True
    raise RuntimeError(f'missing round-authority anchor: {label}')

app,c=any_replace(app,[
'height=int(stats.get("round_height") or info.get("blocks") or mininginfo.get("blocks") or log_job.get("height") or 0);',
'height=int(stats.get("round_height") or info.get("blocks") or mininginfo.get("blocks") or 0);'
],'height=int(log_job.get("round_height") or stats.get("round_height") or info.get("blocks") or mininginfo.get("blocks") or 0);','patched dashboard height precedence: real NEW ROUND first');changed_app|=c

app,c=any_replace(app,[
'job={"job_id":log_job.get("job_id"),"height":stats.get("round_height") or log_job.get("height") or height,"network_diff":network_diff}; job.update(log_job)',
'job={"job_id":log_job.get("job_id"),"height":stats.get("round_height") or log_job.get("round_height") or height,"network_diff":network_diff}; job.update(log_job)'
],'job={"job_id":log_job.get("job_id"),"height":log_job.get("round_height") or height,"network_diff":network_diff}; job.update(log_job)','patched dashboard job height: no synthetic round source');changed_app|=c

round_new='"round":{"height":int(log_job.get("round_height") or height),"shares":round_shares,"work":round_work,"best_share":round_best,"effort_pct":round_effort,"best_share_pct":best_pct,"difficulty":network_diff,"remaining":remaining,"started_at":log_job.get("round_started_at"),"started_epoch":log_job.get("round_started_epoch"),"source":"stratum-log","target_seconds":ROUND_SECONDS}'
app,c=any_replace(app,[
'"round":{"height":int(stats.get("round_height") or height),"shares":round_shares,"work":round_work,"best_share":round_best,"effort_pct":round_effort,"best_share_pct":best_pct,"difficulty":network_diff,"remaining":remaining,"started_at":stats.get("round_started_at"),"target_seconds":ROUND_SECONDS}',
'"round":{"height":int(stats.get("round_height") or height),"shares":round_shares,"work":round_work,"best_share":round_best,"effort_pct":round_effort,"best_share_pct":best_pct,"difficulty":network_diff,"remaining":remaining,"started_at":log_job.get("round_started_at") or stats.get("round_started_at"),"started_epoch":log_job.get("round_started_epoch") or stats.get("round_started_epoch"),"target_seconds":ROUND_SECONDS}'
],round_new,'patched timer: started_at/epoch exclusively from NEW ROUND log');changed_app|=c

# Polling must never create a ROUND STARTED activity.
old_activity="const roundKey=parseTime(r.started_epoch||r.started_at);if(roundKey&&roundKey!==lastRoundKey){lastRoundKey=roundKey;addActivity('round','ROUND STARTED','#'+Number(r.height||0).toLocaleString(),r.started_at?.slice(11)||'',`round-live-${roundKey}`)}"
new_activity="/* ROUND STARTED comes only from /api/logs or the authoritative SSE round event. */"
js,c=any_replace(js,[old_activity],new_activity,'removed synthetic ROUND STARTED activity generator');changed_js|=c

# The SSE round message is authoritative because it is emitted by the real
# Stratum round transition. It may update the activity list, but no polling
# state is allowed to manufacture the event.
old_round_sse="else if(e.type==='round'){window.dispatchEvent(new CustomEvent('fixedcoin:round',{detail:e}));poll(false)}"
new_round_sse="else if(e.type==='round'){addActivity('round','ROUND STARTED','#'+Number(e.height||e.round_height||0).toLocaleString(),String(e.ts||e.time||'').slice(11),`sse-round-${e.height||e.round_height||0}-${e.ts||e.time||''}`);window.dispatchEvent(new CustomEvent('fixedcoin:round',{detail:e}));poll(false)}"
js,c=any_replace(js,[old_round_sse],new_round_sse,'patched realtime round activity from authoritative SSE');changed_js|=c

old_timer="function updateTimer(round){const target=Number(round?.target_seconds)||600,started=parseTime(round?.started_epoch||round?.started_at);if(!started){$('timeRemain').textContent='00:00';$('timePct').textContent='0.0%';$('roundStatus').textContent='WAITING';$('roundStatus').className='status waiting';return}const elapsed=Math.max(0,(Date.now()/1000)-started),remain=Math.max(0,target-elapsed);$('timeRemain').textContent=timeOnly(remain);$('timePct').textContent=(100*remain/target).toFixed(1)+'%';const active=remain>0;$('roundStatus').textContent=active?'ACTIVE':'WAITING';$('roundStatus').className='status '+(active?'active':'waiting')}"
new_timer="function updateTimer(round){const target=Number(round?.target_seconds)||600,started=parseTime(round?.started_epoch||round?.started_at);if(round?.source!=='stratum-log'||!started||started>Date.now()/1000+2){$('timeRemain').textContent='00:00';$('timePct').textContent='0.0%';$('roundStatus').textContent='WAITING';$('roundStatus').className='status waiting';return}const elapsed=Math.max(0,(Date.now()/1000)-started),remain=Math.max(0,target-elapsed);$('timeRemain').textContent=timeOnly(remain);$('timePct').textContent=(100*remain/target).toFixed(1)+'%';const active=remain>0;$('roundStatus').textContent=active?'ACTIVE':'WAITING';$('roundStatus').className='status '+(active?'active':'waiting')}"
js,c=any_replace(js,[old_timer],new_timer,'hardened timer against non-log round timestamps');changed_js|=c

if changed_app:APP.write_text(app)
if changed_js:JS.write_text(js)
print('dashboard round authority verified: only real NEW ROUND log/SSE events can start a round or countdown')
