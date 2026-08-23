#!/usr/bin/env python3
"""Make the animated miner the sole client-side timer/forge-motion owner."""
from pathlib import Path

JS = Path('/app/monitor/static/dashboard_v4.js')
text = JS.read_text()
old = 'setInterval(()=>updateTimer(state?.round||{}),250);'
new = '/* dashboard_v4_miner.js owns the frame-accurate round clock */'
if old in text:
    JS.write_text(text.replace(old, new, 1))
    print('patched dashboard timer ownership: miner realtime clock')
else:
    print('dashboard timer ownership already patched')
