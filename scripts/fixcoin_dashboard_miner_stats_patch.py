#!/usr/bin/env python3
"""Add real per-miner telemetry to LiveShare without fragile JS quoting."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "monitor" / "app.py"
HTML = ROOT / "monitor" / "templates" / "dashboard_v4.html"
CSS = ROOT / "monitor" / "static" / "dashboard_miner_stats.css"
JS = ROOT / "monitor" / "static" / "dashboard_miner_stats.js"

app = APP.read_text(encoding="utf-8")

if "def build_miner_stats(" not in app:
    marker = "def status():\n"
    if marker not in app:
        raise RuntimeError("status marker not found in monitor/app.py")
    helper = """def build_miner_stats(shares, persisted_workers, parsed_workers, now=None):
    \"\"\"Build honest per-worker telemetry from real Stratum share records.\"\"\"
    now = float(now or time.time())
    persisted_workers = persisted_workers if isinstance(persisted_workers, dict) else {}
    parsed_workers = parsed_workers if isinstance(parsed_workers, dict) else {}
    by_worker = {}

    for share in shares if isinstance(shares, list) else []:
        if not isinstance(share, dict):
            continue
        worker = str(share.get(\"worker\") or \"unknown\")
        row = by_worker.setdefault(worker, {\"shares\": [], \"accepted\": 0, \"rejected\": 0})
        row[\"shares\"].append(share)
        row[\"accepted\"] += 1

    for worker, raw in persisted_workers.items():
        if isinstance(raw, dict):
            by_worker.setdefault(str(worker), {\"shares\": [], \"accepted\": 0, \"rejected\": 0})
    for worker, raw in parsed_workers.items():
        if isinstance(raw, dict):
            by_worker.setdefault(str(worker), {\"shares\": [], \"accepted\": 0, \"rejected\": 0})

    def num(v, default=0.0):
        try:
            return float(v)
        except Exception:
            return default

    miners = []
    for worker, row in by_worker.items():
        pv = persisted_workers.get(worker, {}) if isinstance(persisted_workers.get(worker, {}), dict) else {}
        lv = parsed_workers.get(worker, {}) if isinstance(parsed_workers.get(worker, {}), dict) else {}
        recent = [x for x in row.get(\"shares\", []) if isinstance(x, dict) and num(x.get(\"epoch\")) > 0]
        recent5 = [x for x in recent if 0 <= now - num(x.get(\"epoch\")) <= 300 and num(x.get(\"work\")) > 0]
        recent1 = [x for x in recent if 0 <= now - num(x.get(\"epoch\")) <= 60 and num(x.get(\"work\")) > 0]
        h5 = sum(num(x.get(\"work\")) * (2 ** 32) for x in recent5) / 300.0 if recent5 else 0.0
        h1 = sum(num(x.get(\"work\")) * (2 ** 32) for x in recent1) / 60.0 if recent1 else 0.0
        last_epoch = max([num(x.get(\"epoch\")) for x in recent] + [num(lv.get(\"last_seen\"))])
        accepted = int(pv.get(\"ok\") or pv.get(\"accepted\") or lv.get(\"accepted\") or len(recent))
        rejected = int(pv.get(\"bad\") or pv.get(\"rejected\") or lv.get(\"rejected\") or 0)
        total = accepted + rejected
        difficulty = num(pv.get(\"difficulty\") or lv.get(\"difficulty\"), 0.0)
        best = max([num(x.get(\"work\")) for x in recent] + [0.0])
        latest = recent[-1] if recent else {}
        miners.append({
            \"worker\": worker, \"accepted\": accepted, \"rejected\": rejected,
            \"total_shares\": total, \"reject_pct\": round(100.0 * rejected / max(1, total), 3),
            \"hashrate_5m\": h5, \"hashrate_1m\": h1, \"difficulty\": difficulty,
            \"best_share\": best, \"last_share\": latest.get(\"ts\") or \"—\",
            \"last_seen\": last_epoch, \"active\": bool(last_epoch and now - last_epoch <= WORKER_ACTIVE_SECONDS),
            \"vardiff\": bool(lv.get(\"vardiff\") or pv.get(\"vardiff\")),
            \"miner_family\": str(lv.get(\"miner_family\") or pv.get(\"miner_family\") or \"unknown\"),
            \"miner_variant\": str(lv.get(\"miner_variant\") or pv.get(\"miner_variant\") or \"\"),
            \"miner_version\": str(lv.get(\"miner_version\") or pv.get(\"miner_version\") or \"\"),
            \"user_agent\": str(lv.get(\"user_agent\") or pv.get(\"user_agent\") or \"\"),
        })
    miners.sort(key=lambda x: (not x[\"active\"], -x[\"hashrate_5m\"], x[\"worker\"]))
    return miners

"""
    app = app.replace(marker, helper + marker, 1)

if 'miner_stats=build_miner_stats(' not in app:
    needle = '    active_workers=list(workers.keys()); blocks=wallet["blocks"] or (stats.get("blocks_log") if isinstance(stats.get("blocks_log"),list) else []) or log_blocks\n'
    if needle not in app:
        raise RuntimeError("worker status marker not found in monitor/app.py")
    app = app.replace(needle, needle + '    miner_stats=build_miner_stats(shares, persisted, log_workers, time.time())\n', 1)

if '"miners":miner_stats' not in app:
    needle = '"active_workers":active_workers},"round":'
    if needle not in app:
        raise RuntimeError("mining response marker not found in monitor/app.py")
    app = app.replace(needle, '"active_workers":active_workers},"miners":miner_stats,"round":', 1)

APP.write_text(app, encoding="utf-8")

css = """.miners{margin-top:10px;padding:20px 22px;position:relative;overflow:hidden}.miners-head{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:16px}.miners-tools{display:flex;align-items:center;gap:10px}.miners-tools span{font:700 10px/1 JetBrains Mono,monospace;letter-spacing:.12em;color:#59ff9a;border:1px solid rgba(89,255,154,.25);padding:9px 11px;border-radius:8px}.miners-tools select{background:#070b16;color:#d9e7ff;border:1px solid rgba(100,210,255,.22);border-radius:8px;padding:9px 12px;font:700 10px JetBrains Mono,monospace}.miner-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:12px}.miner-card{position:relative;border:1px solid rgba(90,210,255,.14);background:linear-gradient(145deg,rgba(9,15,29,.92),rgba(4,7,15,.82));border-radius:12px;padding:16px;overflow:hidden}.miner-card.active{border-color:rgba(89,255,154,.28);box-shadow:0 0 22px rgba(89,255,154,.06)}.miner-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}.miner-name{font:700 13px JetBrains Mono,monospace;color:#e8f2ff;word-break:break-all}.miner-meta{margin-top:5px;font:9px JetBrains Mono,monospace;color:#70809a}.miner-status{font:700 9px JetBrains Mono,monospace;color:#ff5577;border:1px solid rgba(255,85,119,.2);padding:5px 7px;border-radius:6px}.miner-status.on{color:#59ff9a;border-color:rgba(89,255,154,.25)}.miner-hash{margin:17px 0 13px;font:700 25px JetBrains Mono,monospace;color:#63f4ff}.miner-hash small{font-size:9px;color:#66758e}.miner-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.miner-stat{border:1px solid rgba(100,120,160,.12);border-radius:8px;padding:9px}.miner-stat span{display:block;font:8px JetBrains Mono,monospace;color:#65738a}.miner-stat strong{display:block;margin-top:5px;font:700 12px JetBrains Mono,monospace;color:#dce8fa}.miner-stat.ok strong{color:#59ff9a}.miner-stat.bad strong{color:#ff5577}.miner-bottom{display:flex;justify-content:space-between;gap:10px;margin-top:13px;font:8px JetBrains Mono,monospace;color:#65738a}.miner-bottom b{color:#c8a8ff}.miner-empty{padding:30px;text-align:center;color:#65738a;font:10px JetBrains Mono,monospace;border:1px dashed rgba(100,120,160,.16);border-radius:10px}@media(max-width:700px){.miners-head{align-items:flex-start;flex-direction:column}.miners-tools{width:100%}.miners-tools select{flex:1}.miner-grid{grid-template-columns:1fr}.miner-stats{grid-template-columns:repeat(2,1fr)}}"""
CSS.write_text(css, encoding="utf-8")

js = r'''(()=>{
'use strict';
const fmtHash=n=>{n=Number(n)||0;if(n>=1e12)return(n/1e12).toFixed(2)+' TH/s';if(n>=1e9)return(n/1e9).toFixed(2)+' GH/s';if(n>=1e6)return(n/1e6).toFixed(2)+' MH/s';if(n>=1e3)return(n/1e3).toFixed(2)+' KH/s';return n.toFixed(1)+' H/s'};
const fmt=n=>{n=Number(n)||0;if(n>=1e9)return(n/1e9).toFixed(2)+'B';if(n>=1e6)return(n/1e6).toFixed(2)+'M';if(n>=1e3)return(n/1e3).toFixed(2)+'K';return n.toFixed(n<10?2:0)};
const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
let selected='__all__',cache=[];
function render(){const grid=document.getElementById('minerGrid'),sel=document.getElementById('minerSelect'),badge=document.getElementById('minerCountBadge');if(!grid||!sel)return;badge.textContent=cache.filter(x=>x.active).length+' ONLINE';const ids=new Set([...sel.options].map(o=>o.value));cache.forEach(m=>{if(!ids.has(m.worker)){const o=document.createElement('option');o.value=m.worker;o.textContent=m.worker;sel.appendChild(o)}});if(!cache.length){grid.innerHTML='<div class="miner-empty">No active miner telemetry yet.</div>';return}const rows=selected==='__all__'?cache:cache.filter(x=>x.worker===selected);grid.innerHTML=rows.map(m=>{const family=m.miner_family&&m.miner_family!=='unknown'?`${m.miner_family}${m.miner_variant?'/'+m.miner_variant:''}${m.miner_version?' · '+m.miner_version:''}`:'Stratum client';const last=m.last_share&&m.last_share!=='—'?String(m.last_share).slice(11):'—';return `<article class="miner-card ${m.active?'active':''}"><div class="miner-top"><div><div class="miner-name">${esc(m.worker)}</div><div class="miner-meta">${esc(family)}${m.vardiff?' · VARDIFF':''}</div></div><span class="miner-status ${m.active?'on':''}">${m.active?'ONLINE':'OFFLINE'}</span></div><div class="miner-hash">${fmtHash(m.hashrate_5m)} <small>5M HASHRATE</small></div><div class="miner-stats"><div class="miner-stat ok"><span>Accepted</span><strong>${Number(m.accepted||0).toLocaleString()}</strong></div><div class="miner-stat bad"><span>Rejected</span><strong>${Number(m.rejected||0).toLocaleString()}</strong></div><div class="miner-stat"><span>Reject %</span><strong>${Number(m.reject_pct||0).toFixed(2)}%</strong></div><div class="miner-stat"><span>Difficulty</span><strong>${esc(fmt(m.difficulty))}</strong></div><div class="miner-stat"><span>Best Share</span><strong>${esc(fmt(m.best_share))}</strong></div><div class="miner-stat"><span>1M Rate</span><strong>${fmtHash(m.hashrate_1m)}</strong></div></div><div class="miner-bottom"><span>LAST SHARE <b>${esc(last)}</b></span><span>TYPE <b>${esc(m.miner_variant||m.miner_family||'unknown')}</b></span></div></article>`}).join('')}
window.addEventListener('DOMContentLoaded',()=>{const sel=document.getElementById('minerSelect');if(sel)sel.addEventListener('change',e=>{selected=e.target.value;render()})});
const oldFetch=window.fetch;window.fetch=async function(...args){const r=await oldFetch.apply(this,args);try{const url=String(args[0]||'');if(url.includes('/api/status')){const d=await r.clone().json();cache=Array.isArray(d.miners)?d.miners:[];render()}}catch(_){}return r};
})();
'''
JS.write_text(js, encoding="utf-8")

html = HTML.read_text(encoding="utf-8")
if 'dashboard_miner_stats.css' not in html:
    html = html.replace('</head>', '<link rel="stylesheet" href="/static/dashboard_miner_stats.css?v=20260826-miners2">\n</head>', 1)
if 'id="minersPanel"' not in html:
    section = '''<section class="miners panel" id="minersPanel"><div class="miners-head"><div><h2>MINER ARMORY // LIVE WORKERS</h2><p>Per-miner telemetry from the Stratum share stream.</p></div><div class="miners-tools"><span id="minerCountBadge">0 ONLINE</span><select id="minerSelect" aria-label="Select miner"><option value="__all__">ALL MINERS</option></select></div></div><div class="miner-grid" id="minerGrid"><div class="miner-empty">Waiting for miner telemetry…</div></div></section>\n'''
    marker = '  <section class="candidate panel" id="candidate">'
    if marker not in html:
        raise RuntimeError("candidate section marker not found in dashboard_v4.html")
    html = html.replace(marker, section + marker, 1)
if 'dashboard_miner_stats.js' not in html:
    anchor = '<script defer src="/static/dashboard_v4.js'
    if anchor not in html:
        raise RuntimeError("dashboard_v4.js script anchor not found")
    html = html.replace(anchor, '<script defer src="/static/dashboard_miner_stats.js?v=20260826-miners2"></script>' + anchor, 1)
HTML.write_text(html, encoding="utf-8")

print("dashboard miner stats patch applied: safe Python/JS generation")
