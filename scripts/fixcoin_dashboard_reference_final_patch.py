#!/usr/bin/env python3
"""Install the canonical LiveShare reference dashboard.

All older visual patch layers run before this stage. The final stage replaces
that output with one repository-owned reference template so the production
composition cannot drift back to the legacy dashboard.
"""
from pathlib import Path
import re

ROOT = Path('/app')
TEMPLATE = ROOT / 'monitor/templates/dashboard_v4_reference.html'
HTML = ROOT / 'monitor/templates/dashboard_v4.html'
REFERENCE_CSS = ROOT / 'frontend/app/arcane-reference.css'
VISUAL_CSS = ROOT / 'monitor/static/dashboard_v4_reference_visual.css'
JS = ROOT / 'monitor/static/dashboard_v4.js'
REF_JS = ROOT / 'monitor/static/dashboard_v4_reference_final.js'

html = TEMPLATE.read_text(encoding='utf-8')
css = REFERENCE_CSS.read_text(encoding='utf-8')
VISUAL_CSS.write_text(css + '\n/* monitor runtime safety */\n.reference-dashboard img{max-width:100%;}\n', encoding='utf-8')
HTML.write_text(html, encoding='utf-8')

# Normalize the Chronicle renderer to the eight-column reference layout.
js = JS.read_text(encoding='utf-8')
old = """host.innerHTML=rows.map(b=>{const state=String(b.state||b.status||'').toUpperCase(),valid=state!=='ORPHANED',cls=!valid?'invalid':state==='MATURED'?'valid':'immature',label=!valid?'INVALID / ORPHANED':state==='MATURED'?'VALID · MATURED':'VALID · IMMATURE',conf=Number(b.confirmations||0),target=Number(b.validity_target||100),hash=(b.blockhash||b.txid||'—');return `<div class=\"history-row\"><span>#${Number(b.height||0).toLocaleString()}</span><span><b class=\"validity ${cls}\">${label}</b></span><span>${conf.toLocaleString()} / ${target.toLocaleString()}</span><span>${Number(b.reward||0).toFixed(4)}</span><span title=\"${hash}\">${hash}</span></div>`}).join('')"""
new = """host.innerHTML=rows.map(b=>{const state=String(b.state||b.status||'').toUpperCase(),valid=state!=='ORPHANED',cls=!valid?'invalid':state==='MATURED'?'valid':'immature',label=!valid?'INVALID / ORPHANED':state==='MATURED'?'VALID · MATURED':'VALID · IMMATURE',conf=Number(b.confirmations||0),target=Number(b.validity_target||100),hash=(b.blockhash||b.txid||'—'),time=(b.time||b.ts||b.created_at||'—'),diff=Number(b.difficulty||b.diff||0),luck=Number(b.luck||b.luck_pct||0),shares=Number(b.shares||0),miner=(b.miner||b.worker||'liveshare'),reward=Number(b.reward||0);return `<div class=\"history-row\"><span class=\"height\">#${Number(b.height||0).toLocaleString()}</span><span>${time}</span><span>${fmt(diff)}</span><span class=\"luck\">${luck>0?('+'+luck.toFixed(1)+'%'):'—'}</span><span>${shares.toLocaleString()}</span><span>${miner}</span><span class=\"magicHash\" title=\"${hash}\">${hash}</span><span class=\"reward\">${reward.toFixed(4)}</span></div>`}).join('')"""
if old not in js:
    raise RuntimeError('dashboard reference final: legacy block renderer anchor missing')
JS.write_text(js.replace(old, new, 1), encoding='utf-8')

required_html = [
    'class="liveshareApp reference-dashboard"', 'class="leftRail"', 'class="rightRail"',
    'class="heroPanel ornatePanel"', 'class="dragon dragon-left"', 'class="dragon dragon-right"',
    'id="forgeStage"', 'id="forgeCore"', 'id="particleCanvas"', 'id="targetParticles"',
    'id="candidateParticles"', 'id="acceptedCounter"', 'id="rejectedCounter"', 'id="candidate"',
    'id="candidateCore"', 'id="blockHistoryList"', 'id="historyCount"',
    'dashboard_v4_reference_visual.css', 'dashboard_v4_reference_final.js',
]
missing = [x for x in required_html if x not in html]
for token in ['.liveshareApp', '.heroPanel', '.dragon', '.forgeGrid', '.coreCrystal', '.altarRow', '.historyRow', '.rightRail', '@media(max-width:900px)', '@media(max-width:620px)']:
    if token not in css:
        missing.append('reference css '+token)
ref_js = REF_JS.read_text(encoding='utf-8')
for token in ['syncReferenceTelemetry', 'pointerMove', 'fixedcoin:live']:
    if token not in ref_js:
        missing.append('reference js '+token)
if '<img' in html or '<image' in html or 'dashboard_v4_miner.js' in html:
    raise RuntimeError('dashboard reference final: legacy raster/miner markup found')
ids = re.findall(r'id="([^"]+)"', html)
if len(ids) != len(set(ids)):
    raise RuntimeError('dashboard reference final: duplicate HTML id detected')
if missing:
    raise RuntimeError('dashboard reference final validation failed: '+', '.join(missing))

print('dashboard reference final verified: canonical Arcane LiveShare composition, dual dragons, crystal forge, ornate panels, balance scale, right telemetry rail, Chronicle history, and responsive desktop/mobile layout')
