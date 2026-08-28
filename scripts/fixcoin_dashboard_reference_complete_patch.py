#!/usr/bin/env python3
"""Install the repository-owned responsive Arcane dashboard layer.

The patch is intentionally self-contained and build-safe. It owns only the
reference presentation layer; live data remains supplied by the dashboard
runtime and animations never depend on Discord/GhostBot.
"""
from pathlib import Path

ROOT = Path('/app')
HTML_PATH = ROOT / 'monitor/templates/dashboard_v4.html'
CSS_PATH = ROOT / 'monitor/static/dashboard_v4_reference_complete.css'
JS_PATH = ROOT / 'monitor/static/dashboard_v4_reference_complete.js'

html = HTML_PATH.read_text(encoding='utf-8')

ORNAMENTS = '''
<div id="referenceOrnaments" class="reference-ornaments" aria-hidden="true">
  <div class="arcane-dragon arcane-dragon-left"><i></i></div>
  <div class="arcane-dragon arcane-dragon-right"><i></i></div>
  <div class="arcane-vignette"></div>
</div>
'''

if 'id="referenceOrnaments"' not in html:
    marker = '<main class="dashboard reference-dashboard liveshare-dashboard">'
    if marker in html:
        html = html.replace(marker, ORNAMENTS + marker, 1)

TREASURY = '''
<section class="arcane-treasury panel" id="arcaneTreasury">
  <div class="treasury-head">
    <div class="reference-heading"><span>✦</span><div><h2>ARCANE TREASURY</h2><p>Rewards, pending output and confirmed FixedCoin wealth.</p></div></div>
    <div class="treasury-live"><b></b> WALLET LINKED · LIVE</div>
  </div>
  <div class="treasury-grid">
    <article class="treasury-card"><span>ESTIMATED EARNINGS</span><strong id="estimatedEarnings">—</strong><small>PROJECTED FROM LIVE SHARE FLOW</small><em>✦</em></article>
    <article class="treasury-card pending"><span>PENDING OUTPUT</span><strong id="pendingOutput">—</strong><small>UNCONFIRMED · WAITING FOR TRUST</small><em>◈</em></article>
    <article class="treasury-card paid"><span>TOTAL PAID / REWARDS</span><strong id="totalPaidRewards">—</strong><small>CONFIRMED REWARD HISTORY</small><em>◆</em></article>
    <article class="treasury-card"><span>ARCANE BALANCE</span><strong id="treasuryBalance">—</strong><small>CONFIRMED + PENDING + IMMATURE</small><em>◇</em></article>
  </div>
</section>
<section class="activity-reference panel" id="activityReference">
  <div class="treasury-head"><div class="reference-heading"><span>◈</span><div><h2>RECENT ACTIVITY</h2><p>Live proof-of-work events from the FixedCoin forge.</p></div></div><div class="treasury-live"><b></b> LIVE STREAM</div></div>
  <div class="activity-reference-grid" id="activityReferenceGrid"><div class="activity-reference-empty">Waiting for live share events…</div></div>
</section>
'''

if 'id="arcaneTreasury"' not in html:
    marker = '<section class="block-history panel" id="blockHistory">'
    if marker in html:
        html = html.replace(marker, TREASURY + marker, 1)

OLD = '<div class="history-row history-labels"><span>HEIGHT</span><span>VALIDITY</span><span>CONFIRMATIONS</span><span>REWARD</span><span>BLOCK HASH</span></div>'
NEW = '<div class="history-row history-labels"><span>HEIGHT</span><span>TIME</span><span>DIFFICULTY</span><span>LUCK</span><span>SHARES</span><span>MINER</span><span>BLOCK HASH</span><span>REWARD</span></div>'
html = html.replace(OLD, NEW, 1)

css_tag = '<link rel="stylesheet" href="/static/dashboard_v4_reference_complete.css?v=20260829-2">'
if css_tag not in html:
    html = html.replace('</head>', css_tag + '\n</head>', 1)

js_tag = '<script defer src="/static/dashboard_v4_reference_complete.js?v=20260829-2"></script>'
if js_tag not in html:
    html = html.replace('</body>', js_tag + '\n</body>', 1)

HTML_PATH.write_text(html, encoding='utf-8')

CSS = r'''/* FixedCoin Arcane LiveShare reference layer */
:root{--arc-bg:#010509;--arc-panel:#031016;--arc-cyan:#20e7ff;--arc-green:#54ff82;--arc-red:#ff5367;--arc-gold:#ffbd42;--arc-text:#e9fbfd;--arc-muted:#648089;--arc-mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Consolas,monospace}
.reference-dashboard{width:min(1470px,calc(100vw - 24px));max-width:1470px;margin-inline:auto;gap:12px;position:relative;z-index:1}.reference-dashboard *{box-sizing:border-box}.reference-dashboard .panel{border:1px solid rgba(28,91,105,.78);border-radius:16px;background:linear-gradient(145deg,rgba(4,17,23,.98),rgba(1,6,10,.99));box-shadow:inset 0 0 0 1px rgba(32,230,255,.025),0 22px 70px rgba(0,0,0,.52)}
.reference-ornaments{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden}.arcane-vignette{position:absolute;inset:0;background:radial-gradient(circle at 50% 38%,transparent 0,rgba(0,10,15,.08) 40%,rgba(0,0,0,.58) 100%)}
.arcane-dragon{position:absolute;width:250px;height:165px;opacity:.16;border:1px solid rgba(84,255,130,.5);filter:drop-shadow(0 0 18px rgba(84,255,130,.25));clip-path:polygon(0 58%,17% 44%,27% 18%,42% 39%,58% 6%,68% 37%,100% 25%,84% 59%,100% 73%,69% 66%,54% 96%,43% 67%,22% 91%,28% 65%)}.arcane-dragon-left{left:-55px;top:39vh;transform:rotate(-8deg)}.arcane-dragon-right{right:-55px;top:59vh;transform:scaleX(-1) rotate(-8deg)}.arcane-dragon i{position:absolute;width:8px;height:8px;left:62%;top:39%;border-radius:50%;background:var(--arc-green);box-shadow:0 0 16px var(--arc-green)}
.hero{display:grid!important;grid-template-columns:minmax(0,1fr) clamp(240px,20vw,285px);min-height:clamp(270px,21vw,330px)}.hero-main{min-width:0;padding:clamp(20px,2.2vw,32px)}.hero-values{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);align-items:end;gap:clamp(10px,2vw,28px)}.hero-value strong{font-size:clamp(42px,5vw,74px)!important;line-height:.92}.hero-value span,.hero-value small,.round-panel span,.balance-card span,.stat>span{font-family:var(--arc-mono)}.versus{color:var(--arc-cyan);font:800 clamp(12px,1vw,15px) var(--arc-mono);text-shadow:0 0 16px rgba(32,231,255,.45)}
.target-track,.candidate-track{background:#031218;border:1px solid rgba(27,95,108,.9);box-shadow:inset 0 0 14px rgba(0,0,0,.65)}.target-track i,.candidate-track i{background:linear-gradient(90deg,#21ff72,#1ee6ff);box-shadow:0 0 18px rgba(32,255,117,.5)}
.round-panel{min-width:0;padding:clamp(18px,2vw,28px);border-left:1px solid rgba(27,83,96,.8);background:linear-gradient(180deg,rgba(3,14,20,.98),rgba(1,8,12,.98));display:flex;flex-direction:column;justify-content:center}.round-id{font-size:clamp(26px,2.5vw,40px);color:var(--arc-green);font-family:var(--arc-mono)}.round-panel .remaining{font-size:clamp(28px,2.8vw,42px);color:var(--arc-cyan);font-family:var(--arc-mono)}
.forge-stage{height:clamp(500px,40vw,570px)!important;min-height:0!important}.forge-stage:before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 50% 48%,rgba(54,255,128,.12),transparent 20%),radial-gradient(circle at 50% 52%,rgba(25,225,255,.09),transparent 45%);pointer-events:none;z-index:2}.core-logo{animation:arcFloat 5s ease-in-out infinite}.core-orbit{animation-duration:16s!important}
.arcane-treasury,.activity-reference{padding:clamp(18px,2vw,28px)}.treasury-head{display:flex;align-items:center;justify-content:space-between;gap:18px;margin-bottom:16px}.reference-heading{display:flex;align-items:center;gap:12px}.reference-heading>span{color:var(--arc-cyan);font-size:20px;text-shadow:0 0 16px rgba(32,231,255,.5)}.reference-heading h2{margin:0;color:#dffbff;font:800 clamp(14px,1.2vw,18px) var(--arc-mono);letter-spacing:.12em}.reference-heading p{margin:5px 0 0;color:#5f7b83;font:600 8px var(--arc-mono);letter-spacing:.05em}.treasury-live{color:var(--arc-green);font:700 8px var(--arc-mono);letter-spacing:.12em;white-space:nowrap}.treasury-live b{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--arc-green);box-shadow:0 0 12px var(--arc-green);animation:arcPulse 1.5s infinite;margin-right:6px}.treasury-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.treasury-card{position:relative;min-width:0;min-height:130px;padding:18px;border:1px solid rgba(24,85,99,.78);border-radius:13px;background:linear-gradient(145deg,rgba(4,19,25,.94),rgba(1,7,11,.98));overflow:hidden}.treasury-card>span{display:block;color:#829da4;font:700 8px var(--arc-mono);letter-spacing:.15em}.treasury-card>strong{display:block;margin-top:10px;color:var(--arc-green);font:800 clamp(22px,2vw,30px) var(--arc-mono);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-shadow:0 0 14px rgba(84,255,130,.22)}.treasury-card.pending>strong{color:var(--arc-cyan)}.treasury-card.paid>strong{color:var(--arc-gold)}.treasury-card small{display:block;margin-top:8px;color:#5b747b;font:600 7px var(--arc-mono);letter-spacing:.08em}.treasury-card em{position:absolute;right:17px;bottom:13px;color:rgba(84,255,130,.35);font-style:normal;font-size:28px;text-shadow:0 0 18px rgba(84,255,130,.3)}
.activity-reference-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.activity-reference-row{display:grid;grid-template-columns:34px minmax(0,1fr) auto;align-items:center;gap:10px;min-height:54px;padding:8px 11px;border:1px solid rgba(24,72,84,.65);background:rgba(2,11,15,.72);font-family:var(--arc-mono)}.activity-reference-row .event-icon{display:grid;place-items:center;width:27px;height:27px;border:1px solid currentColor;border-radius:50%;font-weight:800}.activity-reference-row.ok{color:var(--arc-green)}.activity-reference-row.bad{color:var(--arc-red)}.activity-reference-row .event-label{color:#d8ecef;font-size:9px}.activity-reference-row small{display:block;color:#617b82;font-size:7px;margin-top:3px}.activity-reference-row time{color:#5d777e;font-size:8px}.activity-reference-empty{padding:18px;text-align:center;color:#59737b;font:600 9px var(--arc-mono);letter-spacing:.1em}
.history-table{width:100%;overflow:auto}.history-row{display:grid;grid-template-columns:.7fr 1.05fr .95fr .65fr .65fr 1.05fr 2fr .85fr;gap:10px;align-items:center;min-width:930px;padding:11px 10px;border-bottom:1px solid rgba(18,56,66,.55);font-family:var(--arc-mono);font-size:9px}.history-labels{color:#68848b;font-weight:800;font-size:8px;letter-spacing:.12em}
@keyframes arcFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}@keyframes arcPulse{0%,100%{opacity:.45;transform:scale(.85)}50%{opacity:1;transform:scale(1)}}
@media(max-width:1100px){.hero{grid-template-columns:minmax(0,1fr) 240px!important}.treasury-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:760px){.reference-dashboard{width:calc(100vw - 14px)!important;max-width:none!important;gap:9px!important}.hero{display:flex!important;flex-direction:column!important;min-height:0!important}.hero-main{padding:17px!important}.hero-values{grid-template-columns:1fr!important;gap:14px!important}.versus{display:none}.hero-value strong{font-size:clamp(38px,13vw,58px)!important}.round-panel{border-left:0;border-top:1px solid rgba(27,83,96,.8);padding:17px}.forge-stage{height:clamp(430px,115vw,540px)!important}.treasury-grid{grid-template-columns:1fr}.treasury-head{align-items:flex-start;flex-direction:column}.activity-reference-grid{grid-template-columns:1fr}.arcane-dragon{opacity:.1;transform:scale(.65)}.arcane-dragon-right{transform:scaleX(-.65)}.history-row{min-width:900px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important}}
'''
CSS_PATH.write_text(CSS, encoding='utf-8')

JS = r'''(() => {
  const $ = id => document.getElementById(id);
  const pick = (o, paths) => { for (const p of paths) { let v=o; for (const k of p.split('.')) v=v?.[k]; if(v!==undefined&&v!==null&&v!=='') return v; } return null; };
  const num = v => Number.isFinite(Number(v)) ? Number(v) : 0;
  const fmt = v => num(v).toLocaleString(undefined,{maximumFractionDigits:8});
  const set = (id,v) => { const e=$(id); if(e) e.textContent=v==null?'—':String(v); };
  function treasury(s){
    const confirmed=pick(s,['wallet.confirmed','wallet.confirmed_balance','balances.confirmed','confirmed_balance']);
    const pending=pick(s,['wallet.unconfirmed','wallet.unconfirmed_balance','wallet.pending','balances.unconfirmed','unconfirmed_balance']);
    const immature=pick(s,['wallet.immature','wallet.immature_balance','balances.immature','immature_balance']);
    const total=pick(s,['wallet.total','wallet.total_balance','balances.total','total_balance']);
    const estimated=pick(s,['earnings.estimated','earnings.estimated_earnings','estimated_earnings','wallet.estimated_earnings']);
    const paid=pick(s,['earnings.total_paid','earnings.paid','wallet.total_paid','total_paid','rewards.total_paid']);
    set('estimatedEarnings',estimated==null?'—':fmt(estimated)+' FX');
    set('pendingOutput',pending==null?'—':fmt(pending)+' FX');
    set('totalPaidRewards',paid==null?'—':fmt(paid)+' FX');
    const balance=total!=null?total:(confirmed!=null?num(confirmed)+num(pending)+num(immature):null);
    set('treasuryBalance',balance==null?'—':fmt(balance)+' FX');
  }
  function activity(s){
    const grid=$('activityReferenceGrid'); if(!grid)return;
    const items=pick(s,['activity','recent_activity','events','recentActivity']);
    if(!Array.isArray(items))return;
    grid.replaceChildren(...items.slice(0,12).map((x,i)=>{
      const row=document.createElement('div'); row.className='activity-reference-row '+(String(x.type||x.status||'').toLowerCase().includes('reject')?'bad':'ok');
      row.innerHTML='<span class="event-icon">'+(row.classList.contains('bad')?'×':'✓')+'</span><div><div class="event-label">'+String(x.label||x.type||'SHARE ACCEPTED')+'</div><small>'+String(x.worker||x.miner||x.message||'FixedCoin forge event')+'</small></div><time>'+String(x.time||x.ts||'LIVE')+'</time>';
      return row;
    }));
  }
  async function poll(){try{const r=await fetch('/api/status?ts='+Date.now(),{cache:'no-store'});if(!r.ok)return;const s=await r.json();treasury(s);activity(s);}catch(_){}}
  poll(); setInterval(poll,2000);
})();
'''
JS_PATH.write_text(JS, encoding='utf-8')

# Fail fast on syntax errors in this patch itself; compile the source text once.
source = Path(__file__).read_text(encoding='utf-8')
compile(source, str(__file__), 'exec')
print('dashboard complete reference installed: responsive desktop/mobile, Arcane Treasury, activity, Chronicle layout, depth, glow and motion')
