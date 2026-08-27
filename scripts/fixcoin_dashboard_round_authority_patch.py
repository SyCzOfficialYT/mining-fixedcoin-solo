#!/usr/bin/env python3
"""Make dashboard round/timer state originate only from real NEW ROUND state."""
from pathlib import Path
import re

APP=Path('/app/monitor/app.py'); JS=Path('/app/monitor/static/dashboard_v4.js')
app=APP.read_text(); js=JS.read_text(); changed_app=False; changed_js=False

# parse_logs() stores the live Stratum NEW ROUND/job height as log_job["height"].
# stats.json may contain an older round_height after a restart and must never
# override the live Stratum height.
height_re=r'(?m)^    height=int\([^\n]+\);'
height_match=re.search(height_re,app)
if height_match:
    authoritative='    height=int(log_job.get("height") or stats.get("round_height") or info.get("blocks") or mininginfo.get("blocks") or 0);'
    if height_match.group(0)!=authoritative:
        app=app[:height_match.start()]+authoritative+app[height_match.end():]
        changed_app=True
        print('patched dashboard height precedence: live Stratum NEW ROUND/job first')

# Capture the timestamp of the actual NEW ROUND log event.
new_round_re=r'(?m)^        if m: job\["height"\]=int\(m\.group\(1\)\); job\["network_diff"\]=float\(m\.group\(2\)\)'
new_round_match=re.search(new_round_re,app)
if new_round_match:
    new='        if m:\n            job["height"]=int(m.group(1)); job["network_diff"]=float(m.group(2)); job["round_started_at"]=line[:19]; job["round_started_epoch"]=ts'
    app=app[:new_round_match.start()]+new+app[new_round_match.end():]
    changed_app=True
    print('patched NEW ROUND timestamp authority: live log timestamp exported')

round_pat=r'"round":\{"height":.*?"target_seconds":ROUND_SECONDS\}'
rm=re.search(round_pat,app)
if rm:
    old=rm.group(0)
    new=(old
         .replace('"height":int(stats.get("round_height") or height)',
                  '"height":int(log_job.get("height") or stats.get("round_height") or height)')
         .replace('"height":int(log_job.get("round_height") or height)',
                  '"height":int(log_job.get("height") or stats.get("round_height") or height)')
         .replace('"started_at":stats.get("round_started_at")',
                  '"started_at":log_job.get("round_started_at") or stats.get("round_started_at")')
         .replace('"target_seconds":ROUND_SECONDS',
                  '"started_epoch":log_job.get("round_started_epoch") or stats.get("round_started_epoch"),"source":"stratum-log","target_seconds":ROUND_SECONDS'))
    if new!=old:
        app=app.replace(old,new,1)
        changed_app=True
        print('patched dashboard timer source: NEW ROUND log')

job_re=r'job=\{"job_id":log_job\.get\("job_id"\),"height":[^\n]+,"network_diff":network_diff\}; job\.update\(log_job\)'
job_match=re.search(job_re,app)
if job_match:
    authoritative_job='job={"job_id":log_job.get("job_id"),"height":log_job.get("height") or stats.get("round_height") or height,"network_diff":network_diff}; job.update(log_job)'
    if job_match.group(0)!=authoritative_job:
        app=app[:job_match.start()]+authoritative_job+app[job_match.end():]
        changed_app=True
        print('patched final job height authority')

round_re=r'"round":\{"height":[^,]+,"shares":round_shares'
round_match=re.search(round_re,app)
if round_match:
    authoritative_round='"round":{"height":int(log_job.get("height") or stats.get("round_height") or height),"shares":round_shares'
    if round_match.group(0)!=authoritative_round:
        app=app[:round_match.start()]+authoritative_round+app[round_match.end():]
        changed_app=True
        print('patched final round object authority')

if changed_app: APP.write_text(app)

# Frontend: round timer is an estimate anchored to the real NEW ROUND event.
# It must never roll back to 10:00 on every poll and must not clamp silently at
# zero. After the target interval it shows an explicit +MM:SS overrun until a
# genuinely new NEW ROUND event changes started_epoch.
old_timer="function updateTimer(round){const target=Number(round?.target_seconds)||600,started=parseTime(round?.started_epoch||round?.started_at);"
new_timer="function updateTimer(round){const target=Number(round?.target_seconds)||600,started=parseTime(round?.started_epoch||round?.started_at);"
if old_timer in js:
    # Replace the complete function body up to seedLogs. This keeps the timer
    # implementation deterministic even if an earlier patch installed a
    # different zero-state branch.
    start=js.index(old_timer)
    end=js.index("function seedLogs",start)
    replacement="""function updateTimer(round){const target=Number(round?.target_seconds)||600,started=parseTime(round?.started_epoch||round?.started_at);const remainEl=$('timeRemain'),pctEl=$('timePct'),statusEl=$('roundStatus');if(!started){remainEl.textContent='—';pctEl.textContent='0.0%';statusEl.textContent='WAITING FOR ROUND';statusEl.className='status waiting';return}const elapsed=Math.max(0,(Date.now()/1000)-started);const remain=Math.max(0,target-elapsed);const overrun=Math.max(0,elapsed-target);if(overrun>0){remainEl.textContent='+'+timeOnly(overrun);pctEl.textContent='OVERRUN';statusEl.textContent='OVERRUN';statusEl.className='status active'}else{remainEl.textContent=timeOnly(remain);pctEl.textContent=(100*remain/target).toFixed(1)+'%';statusEl.textContent='ACTIVE';statusEl.className='status active'}}\n"""
    js=js[:start]+replacement+js[end:]
    changed_js=True

if changed_js: JS.write_text(js)

print('dashboard round authority patch complete: live NEW ROUND epoch, bounded countdown, explicit overrun')