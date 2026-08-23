#!/usr/bin/env python3
"""Install the high-fidelity articulated miner implementation."""
from pathlib import Path

src=Path('/app/monitor/static/dashboard_v4_miner_v3.js')
dst=Path('/app/monitor/static/dashboard_v4_miner.js')
text=src.read_text()
required=['miner-puppet-v3','function strike(kind=','fixedcoin:accept','fixedcoin:reject','fixedcoin:block','class="hammer"','class="upper-arm"','class="forearm"','class="shoulder"']
missing=[x for x in required if x not in text]
if missing:
    raise RuntimeError('miner v3 source incomplete: '+', '.join(missing))
dst.write_text(text)
print('dashboard miner v3 installed: articulated industrial miner, human-like body/arm/hammer swing, impact timing, no raster image')
