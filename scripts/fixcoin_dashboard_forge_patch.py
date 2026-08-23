#!/usr/bin/env python3
"""Make FIXCORE the only forge visualization in dashboard_v4."""
from pathlib import Path
import re

HTML=Path('/app/monitor/templates/dashboard_v4.html')
html=HTML.read_text()
# Remove any legacy humanoid/raster miner mount left by older patches.
html=re.sub(r'\s*<div class="miner-reference-wrap"[^>]*>.*?</div>', '', html, count=1, flags=re.S)
html=re.sub(r'\s*<script[^>]+dashboard_v4_miner\.js[^>]*></script>', '', html, count=1)
# Remove the old anvil/impact markup if an older patch inserted it.
html=re.sub(r'\s*<div class="anvil"[^>]*>.*?</div>\s*<div class="impact"[^>]*>.*?</div>', '', html, count=1, flags=re.S)
if 'id="forgeCore"' not in html:
    raise RuntimeError('FIXCORE mount missing after legacy miner cleanup')
if 'dashboard_v4_miner.js' in html or 'miner-reference' in html or '<img' in html or '<image' in html:
    raise RuntimeError('legacy miner markup survived FIXCORE dashboard patch')
HTML.write_text(html)
print('FIXCORE forge enforced: legacy humanoid/raster miner removed from dashboard template')
