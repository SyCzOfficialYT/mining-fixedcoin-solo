#!/usr/bin/env python3
"""Make dashboard round/timer state originate only from real NEW ROUND state."""
from pathlib import Path
import re

APP = Path('/app/monitor/app.py')
JS = Path('/app/monitor/static/dashboard_v4.js')
HTML = Path('/app/monitor/templates/dashboard_liveshare.html')

app = APP.read_text()
js = JS.read_text()
changed_app = False
changed_js = False
changed_html = False

# The live Stratum NEW ROUND event is authoritative. stats.json can survive a
# restart with an older round and therefore must never win over the live log.
height_re = r'(?m)^    height=int\([^\n]+\);'
height_match = re.search(height_re, app)
if height_match:
    authoritative = '    height=int(log_job.get("height") or stats.get("round_height") or info.get("blocks") or mininginfo.get("blocks") or 0);'
    if height_match.group(0) != authoritative:
        app = app[:height_match.start()] + authoritative + app[height_match.end():]
        changed_app = True
        print('patched dashboard height precedence: live Stratum NEW ROUND/job first')

# Export the exact timestamp of the NEW ROUND event. This is the only clock
# origin the frontend countdown is allowed to use.
new_round_re = r'(?m)^        if m: job\["height"\]=int\(m\.group\(1\)\); job\["network_diff"\]=float\(m\.group\(2\)\)'
new_round_match = re.search(new_round_re, app)
if new_round_match:
    new = (
        '        if m:\n'
        '            job["height"]=int(m.group(1)); job["network_diff"]=float(m.group(2)); '
        'job["round_started_at"]=line[:19]; job["round_started_epoch"]=ts'
    )
    app = app[:new_round_match.start()] + new + app[new_round_match.end():]
    changed_app = True
    print('patched NEW ROUND timestamp authority: live log timestamp exported')

round_pat = r'"round":\{"height":.*?"target_seconds":ROUND_SECONDS\}'
rm = re.search(round_pat, app)
if rm:
    old = rm.group(0)
    new = (
        old
        .replace(
            '"height":int(stats.get("round_height") or height)',
            '"height":int(log_job.get("height") or stats.get("round_height") or height)',
        )
        .replace(
            '"height":int(log_job.get("round_height") or height)',
            '"height":int(log_job.get("height") or stats.get("round_height") or height)',
        )
        .replace(
            '"started_at":stats.get("round_started_at")',
            '"started_at":log_job.get("round_started_at") or stats.get("round_started_at")',
        )
        .replace(
            '"target_seconds":ROUND_SECONDS',
            '"started_epoch":log_job.get("round_started_epoch") or stats.get("round_started_epoch"),"source":"stratum-log","target_seconds":ROUND_SECONDS',
        )
    )
    if new != old:
        app = app.replace(old, new, 1)
        changed_app = True
        print('patched dashboard timer source: NEW ROUND log')

job_re = r'job=\{"job_id":log_job\.get\("job_id"\),"height":[^\n]+,"network_diff":network_diff\}; job\.update\(log_job\)'
job_match = re.search(job_re, app)
if job_match:
    authoritative_job = (
        'job={"job_id":log_job.get("job_id"),"height":log_job.get("height") or '
        'stats.get("round_height") or height,"network_diff":network_diff}; job.update(log_job)'
    )
    if job_match.group(0) != authoritative_job:
        app = app[:job_match.start()] + authoritative_job + app[job_match.end():]
        changed_app = True
        print('patched final job height authority')

round_re = r'"round":\{"height":[^,]+,"shares":round_shares'
round_match = re.search(round_re, app)
if round_match:
    authoritative_round = (
        '"round":{"height":int(log_job.get("height") or stats.get("round_height") or height),'
        '"shares":round_shares'
    )
    if round_match.group(0) != authoritative_round:
        app = app[:round_match.start()] + authoritative_round + app[round_match.end():]
        changed_app = True
        print('patched final round object authority')

if changed_app:
    APP.write_text(app)

# Replace the complete frontend timer function, rather than depending on one
# exact previous implementation. This makes the build patch idempotent and
# prevents a later dashboard patch from silently restoring the old behaviour.
#
# Rules:
#   * countdown starts only from the actual NEW ROUND epoch;
#   * never resets to 10:00 merely because /api/status was polled;
#   * at zero, explicitly enters OVERRUN and continues as +MM:SS;
#   * a new NEW ROUND epoch naturally resets the timer.
timer_re = r'function updateTimer\(round\)\{.*?\}\nfunction seedLogs'
timer_match = re.search(timer_re, js, re.S)
if timer_match:
    replacement = '''function updateTimer(round){
  const target=Math.max(1,Number(round?.target_seconds)||600);
  const started=parseTime(round?.started_epoch||round?.started_at);
  const remainEl=$('timeRemain'), pctEl=$('timePct'), statusEl=$('roundStatus');
  if(!remainEl||!pctEl||!statusEl)return;
  if(!started){
    remainEl.textContent='—';
    pctEl.textContent='0.0%';
    statusEl.textContent='WAITING FOR ROUND';
    statusEl.className='status waiting';
    return;
  }
  const elapsed=Math.max(0,(Date.now()/1000)-started);
  const remain=target-elapsed;
  if(remain<=0){
    const overrun=Math.floor(Math.abs(remain));
    remainEl.textContent='+'+timeOnly(overrun);
    pctEl.textContent='OVERRUN';
    statusEl.textContent='OVERRUN';
    statusEl.className='status active overrun';
    return;
  }
  remainEl.textContent=timeOnly(remain);
  pctEl.textContent=(100*remain/target).toFixed(1)+'%';
  statusEl.textContent='ACTIVE';
  statusEl.className='status active';
}
function seedLogs'''
    js = js[:timer_match.start()] + replacement + js[timer_match.end():]
    changed_js = True
    print('patched frontend timer: NEW ROUND countdown + explicit overrun')

if changed_js:
    JS.write_text(js)

# Remove the misleading hard-coded label and make the duration field explicit.
# The actual target remains ROUND_TARGET_SECONDS (normally 600 seconds), while
# the live Time Remaining field is driven exclusively by NEW ROUND.
if HTML.exists():
    html = HTML.read_text()
    old_label = '<span class="ls-label">Round Time</span>\n      <b>10:00</b>'
    new_label = '<span class="ls-label">Round Target</span>\n      <b id="roundTarget">10:00</b>'
    if old_label in html:
        html = html.replace(old_label, new_label, 1)
        changed_html = True
        print('patched dashboard round label: target duration, not elapsed round time')
    if changed_html:
        HTML.write_text(html)

print('dashboard round authority patch complete: live NEW ROUND epoch, deterministic countdown, explicit overrun')
