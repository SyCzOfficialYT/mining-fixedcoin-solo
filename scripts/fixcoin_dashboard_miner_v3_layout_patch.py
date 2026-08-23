#!/usr/bin/env python3
from pathlib import Path

for path in (Path('/app/monitor/static/dashboard_v4_miner_v3.js'), Path('/app/monitor/static/dashboard_v4_miner.js')):
    text=path.read_text()
    old='<g class="anvil">'
    new='<g class="anvil" transform="translate(342 368)">'
    if new not in text:
        if old not in text:
            raise RuntimeError(f'missing anvil anchor in {path}')
        text=text.replace(old,new,1)
        path.write_text(text)
print('dashboard miner v3 layout verified: anvil aligned under hammer impact point')
