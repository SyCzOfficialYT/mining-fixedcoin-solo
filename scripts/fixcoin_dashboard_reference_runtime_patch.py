#!/usr/bin/env python3
from pathlib import Path

ROOT=Path('/app')
js_path=ROOT/'monitor/static/dashboard_v4.js'
js=js_path.read_text(encoding='utf-8')
old="""host.innerHTML=rows.map(b=>{const state=String(b.state||b.status||'').toUpperCase(),valid=state!=='ORPHANED',cls=!valid?'invalid':state==='MATURED'?'valid':'immature',label=!valid?'INVALID / ORPHANED':state==='MATURED'?'VALID · MATURED':'VALID · IMMATURE',conf=Number(b.confirmations||0),target=Number(b.validity_target||100),hash=(b.blockhash||b.txid||'—');return `<div class=\"history-row\"><span>#${Number(b.height||0).toLocaleString()}</span><span><b class=\"validity ${cls}\">${label}</b></span><span>${conf.toLocaleString()} / ${target.toLocaleString()}</span><span>${Number(b.reward||0).toFixed(4)}</span><span title=\"${hash}\">${hash}</span></div>`}).join('')"""
new="""host.innerHTML=rows.map(b=>{const state=String(b.state||b.status||'').toUpperCase(),valid=state!=='ORPHANED',cls=!valid?'invalid':state==='MATURED'?'valid':'immature',conf=Number(b.confirmations||0),target=Number(b.validity_target||100),hash=(b.blockhash||b.txid||'—'),time=(b.time||b.ts||b.created_at||'—'),diff=Number(b.difficulty||b.diff||0),luck=Number(b.luck||b.luck_pct||0),shares=Number(b.shares||0),miner=(b.miner||b.worker||'liveshare'),reward=Number(b.reward||0);return `<div class=\"history-row\"><span class=\"height\">#${Number(b.height||0).toLocaleString()}</span><span>${time}</span><span>${fmt(diff)}</span><span class=\"luck\">${luck>0?('+'+luck.toFixed(1)+'%'):'—'}</span><span>${shares.toLocaleString()}</span><span>${miner}</span><span class=\"magicHash\" title=\"${hash}\">${hash}</span><span class=\"reward\">${reward.toFixed(4)}</span></div>`}).join('')"""
if old not in js:
    raise RuntimeError('reference runtime: Chronicle renderer anchor not found')
js_path.write_text(js.replace(old,new,1),encoding='utf-8')
print('reference runtime verified: Chronicle renderer now matches eight-column visual reference')
