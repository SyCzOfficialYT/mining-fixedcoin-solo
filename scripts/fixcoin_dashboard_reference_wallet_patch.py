#!/usr/bin/env python3
"""Populate the five reference balance/rate cards from the existing /api/status wallet state."""
from pathlib import Path

JS = Path('/app/monitor/static/dashboard_v4.js')
s = JS.read_text()

anchor = "const duration=sec=>{sec=Math.max(0,Math.floor(Number(sec)||0));const d=Math.floor(sec/86400),h=Math.floor(sec%86400/3600),m=Math.floor(sec%3600/60),s=sec%60;if(d)return`~${d}d ${h}h`;return`${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`};"
insert = anchor + "\nconst fixBalance=v=>{const n=Number(v)||0;return n.toFixed(8)+' FIX'};"
if "const fixBalance=" not in s:
    if anchor not in s:
        raise RuntimeError('reference wallet patch: duration helper anchor missing')
    s=s.replace(anchor,insert,1)

anchor2 = "$('uptime').textContent=uptime(s.uptime_seconds);"
insert2 = anchor2 + "const w=s.wallet||{};$('confirmedBalance').textContent=fixBalance(w.confirmed);$('unconfirmedBalance').textContent=fixBalance(w.unconfirmed);$('immatureBalance').textContent=fixBalance(w.immature);$('totalBalance').textContent=fixBalance(w.total);"
if "$('confirmedBalance').textContent" not in s:
    if anchor2 not in s:
        raise RuntimeError('reference wallet patch: uptime render anchor missing')
    s=s.replace(anchor2,insert2,1)

JS.write_text(s)
print('dashboard reference wallet patch applied: confirmed/unconfirmed/immature/total balance cards wired')
