#!/usr/bin/env python3
"""Finish the Liveshare dashboard visual composition against the Arcane reference.

This is intentionally presentation-only: it does not change mining, RPC, wallet,
or share validation logic. It enriches the existing Liveshare template with the
missing reference rail cards and appends a final CSS/JS visual layer.
"""
from pathlib import Path

HTML = Path('/app/monitor/templates/dashboard_liveshare.html')
CSS = Path('/app/monitor/static/dashboard_liveshare.css')
JS = Path('/app/monitor/static/dashboard_liveshare_arcane.js')

html = HTML.read_text(encoding='utf-8')
marker = '<!-- ARCANE_REFERENCE_RAIL -->'
if marker not in html:
    needle = '''    <div class="panel round">\n      <span class="ls-label">Current Round</span>'''
    replacement = '''    <div class="panel round">\n      <span class="ls-label">Current Round</span>'''
    if needle not in html:
        raise SystemExit('Liveshare round panel anchor not found')
    html = html.replace(needle, replacement, 1)

    needle2 = '''    <div class="panel">\n      <span class="ls-label">Workers Online</span>\n      <strong id="workerCount">0</strong>\n      <small>Connected</small>\n    </div>'''
    rail = '''    <!-- ARCANE_REFERENCE_RAIL -->\n    <div class="panel rail-economy purple-rail">\n      <span class="ls-label">Estimated Earnings</span>\n      <strong id="railEstimated">0.00000000 FIX</strong>\n      <small>Round rewards projection</small>\n    </div>\n    <div class="panel rail-economy ok-rail">\n      <span class="ls-label">Pending Payout</span>\n      <strong id="railPending">0.00000000 FIX</strong>\n      <small>Untrusted / pending</small>\n    </div>\n    <div class="panel rail-economy cyan-rail">\n      <span class="ls-label">Total Paid / Rewards</span>\n      <strong id="railPaid">0.00000000 FIX</strong>\n      <small>Recorded rewards</small>\n    </div>\n    <div class="panel rail-system">\n      <span class="ls-label">Workers Online</span>\n      <strong id="workerCount">0</strong>\n      <small>Connected</small>\n    </div>\n    <div class="panel rail-system">\n      <span class="ls-label">Server Time</span>\n      <strong id="railServerTime">--:--:--</strong>\n      <small>Local node time</small>\n    </div>'''
    if needle2 not in html:
        raise SystemExit('Workers rail anchor not found')
    html = html.replace(needle2, rail, 1)

    html = html.replace(
        '<div class="history-head"><h2>Block History</h2><p>Chronicles of the Eternal Chain</p><span class="count" id="historyCount">0 RECORDS</span></div>',
        '<div class="history-head"><div class="history-title"><span class="history-sigil">✦</span><div><h2>Chronicles of the FixedCoin Chain</h2><p>Validated blocks · arcane confirmations · rewards · proof history</p></div></div><span class="count" id="historyCount">0 RECORDS</span></div>'
    )
    html = html.replace(
        '<div class="tr head"><span>Height</span><span>Validity</span><span>Confirmations</span><span>Reward</span><span>Block Hash</span></div>',
        '<div class="tr head"><span>Height</span><span>Time</span><span>Arcane Confirmations</span><span>Reward</span><span>Magic Hash</span></div>'
    )
    html = html.replace(
        '<script defer src="/static/dashboard_liveshare.js?v=20260826-fantasy1"></script>',
        '<script defer src="/static/dashboard_liveshare.js?v=20260826-fantasy1"></script>\n<script defer src="/static/dashboard_liveshare_arcane.js?v=20260827-arcane1"></script>'
    )
    HTML.write_text(html, encoding='utf-8')
    print('Liveshare reference rail/history markup applied.')
else:
    print('Liveshare reference rail/history markup already applied.')

CSS_LAYER = r'''

/* ================================================================
   ARCANE REFERENCE FINISH — visual-only layer
   ================================================================ */
:root {
  --arcane-violet: #b66cff;
  --arcane-blue: #38bdf8;
  --arcane-gold: #e7bd58;
  --arcane-green: #61e294;
  --arcane-red: #ff5964;
  --arcane-border: rgba(125, 95, 190, .52);
}

html, body { background:#03030c; }
body::before {
  content:"";
  position:fixed;
  inset:0;
  pointer-events:none;
  z-index:0;
  opacity:.42;
  background:
    linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.014) 1px, transparent 1px),
    radial-gradient(circle at 50% 34%, rgba(101,50,205,.16), transparent 30%),
    radial-gradient(circle at 88% 22%, rgba(20,110,180,.11), transparent 25%),
    radial-gradient(circle at 10% 76%, rgba(108,45,180,.12), transparent 28%);
  background-size: 46px 46px, 46px 46px, auto, auto, auto;
}

.ls-shell {
  isolation:isolate;
  grid-template-columns:150px minmax(0,1fr) 205px;
  gap:8px;
  padding:6px;
  background:
    radial-gradient(ellipse at 50% -10%, rgba(115,48,220,.25), transparent 43%),
    radial-gradient(ellipse at 8% 85%, rgba(75,32,155,.13), transparent 28%),
    radial-gradient(ellipse at 100% 45%, rgba(30,120,180,.10), transparent 26%),
    #03030c;
}

.panel,.card {
  position:relative;
  overflow:hidden;
  border:1px solid var(--arcane-border);
  border-radius:11px;
  background:
    linear-gradient(135deg, rgba(18,13,42,.96), rgba(4,4,15,.98) 62%, rgba(10,7,28,.96));
  box-shadow:
    inset 0 1px rgba(255,255,255,.035),
    inset 0 0 34px rgba(89,55,150,.055),
    0 10px 28px rgba(0,0,0,.42);
}
.panel::before,.card::before {
  content:"";
  position:absolute;
  inset:3px;
  border:1px solid rgba(212,175,90,.045);
  border-radius:8px;
  pointer-events:none;
}
.panel::after {
  content:"✦";
  position:absolute;
  top:5px;
  right:8px;
  color:rgba(212,175,90,.16);
  font:10px var(--display);
  pointer-events:none;
}

/* The reference has a framed, ceremonial navigation column. */
.ls-side {
  padding:11px 8px;
  border-color:rgba(212,175,90,.28);
  background:
    radial-gradient(circle at 50% 72%, rgba(100,43,180,.13), transparent 25%),
    linear-gradient(180deg,#100923,#04030e 72%);
  box-shadow:inset -1px 0 rgba(212,175,90,.12), 0 0 30px rgba(0,0,0,.55);
}
.ls-brand {
  justify-content:center;
  text-align:center;
  flex-direction:column;
  gap:5px;
  padding-bottom:10px;
  border-bottom:1px solid rgba(212,175,90,.2);
}
.ls-brand svg { width:44px; height:44px; filter:drop-shadow(0 0 10px rgba(167,139,250,.5)); }
.ls-brand strong { font-size:10px; letter-spacing:.22em; }
.ls-brand span { font-size:8px; letter-spacing:.18em; }
.ls-side nav button {
  position:relative;
  min-height:39px;
  border:1px solid transparent;
  padding:7px 8px;
  font-size:9px;
  letter-spacing:.13em;
  transition:all .2s ease;
}
.ls-side nav button::before { content:"◇"; color:rgba(212,175,90,.5); margin-right:2px; }
.ls-side nav button.active {
  border-color:rgba(167,139,250,.28);
  background:linear-gradient(90deg,rgba(124,58,237,.26),rgba(18,11,45,.15));
  box-shadow:inset 2px 0 #b66cff, 0 0 18px rgba(124,58,237,.12);
}
.ls-side-gem { min-height:150px; position:relative; }
.ls-side-gem::after {
  content:"";
  position:absolute;
  width:84px;height:18px;
  bottom:7px;left:50%;transform:translateX(-50%);
  background:radial-gradient(ellipse,rgba(151,84,255,.55),transparent 68%);
  filter:blur(5px);
}
.ls-node { font-size:9px; }
.ls-node .ok { text-shadow:0 0 12px rgba(74,222,128,.45); }

/* Wide ceremonial hero: dragons, runes, central title, VS medallion. */
.ls-hero {
  flex:0 0 255px;
  min-height:255px;
  grid-template-columns:150px minmax(0,1fr) 150px;
  border-color:rgba(212,175,90,.30);
  background:
    radial-gradient(circle at 50% 60%,rgba(113,52,208,.15),transparent 36%),
    linear-gradient(180deg,rgba(17,11,42,.97),rgba(4,4,14,.98));
}
.ls-hero::before {
  inset:6px;
  border-color:rgba(212,175,90,.10);
}
.ls-hero-art { z-index:1; }
.dragon {
  width:145px;
  height:215px;
  opacity:.95;
  filter:drop-shadow(0 0 18px rgba(125,67,240,.48)) drop-shadow(0 0 35px rgba(40,160,255,.08));
  animation:dragonFloat 7s ease-in-out infinite;
}
.dragon.flip { animation-delay:-3.5s; }
.hero-gem { width:58px;height:78px; bottom:9px; }
.ls-hero-center { z-index:2; }
.kicker { color:#a99bc9; font-size:9px; letter-spacing:.38em; }
.ls-hero-center h1 {
  font-size:clamp(34px,4vw,56px);
  letter-spacing:.38em;
  margin:3px 0 15px;
  color:#eee3ff;
  text-shadow:0 0 14px rgba(182,108,255,.7),0 0 38px rgba(91,53,180,.35);
}
.ls-hero-center h1::after {
  content:"SOLO MINING · MAGICAL NETWORK";
  display:block;
  margin-top:7px;
  font:7px var(--display);
  letter-spacing:.34em;
  color:#b8a3cf;
}
.versus { grid-template-columns:minmax(0,1fr) 76px minmax(0,1fr); gap:10px; }
.stat strong { font-size:clamp(25px,2.8vw,38px); }
.stat small,.bar-cap,.stat em { font-size:8px; }
.compass {
  width:72px;height:72px;
  border-color:rgba(212,175,90,.75);
  box-shadow:0 0 0 4px rgba(212,175,90,.045),0 0 24px rgba(212,175,90,.20), inset 0 0 18px rgba(212,175,90,.09);
}
.compass::before,.compass::after {
  content:""; position:absolute; width:52px;height:52px; border:1px solid rgba(167,139,250,.22); transform:rotate(45deg);
}
.compass { position:relative; }
.compass::after { width:42px;height:42px; border-color:rgba(212,175,90,.22); }
.bar { height:7px; background:rgba(3,3,12,.85); }
.bar::after {
  content:"";position:absolute;inset:1px;
  background:repeating-linear-gradient(90deg,transparent 0 24px,rgba(167,139,250,.08) 25px 26px);
  pointer-events:none;
}

/* Forge becomes the luminous central altar from the reference. */
.ls-forge {
  flex:1 1 auto;
  min-height:300px;
  grid-template-columns:minmax(160px,.82fr) minmax(260px,1.35fr) minmax(160px,.82fr);
  gap:9px;
  padding:9px;
  background:
    radial-gradient(circle at 50% 60%,rgba(93,45,185,.16),transparent 31%),
    linear-gradient(180deg,rgba(7,6,20,.98),rgba(3,3,11,.99));
}
.ls-forge .col { gap:9px; }
.ls-forge .card {
  padding:11px 12px;
  background:linear-gradient(180deg,rgba(12,9,29,.93),rgba(3,4,13,.98));
}
.ls-forge .card strong { font-size:22px; }
.ls-forge .card:hover { border-color:rgba(167,139,250,.55); box-shadow:0 0 22px rgba(110,60,190,.10), inset 0 0 20px rgba(110,60,190,.05); }
.core {
  border-color:rgba(112,77,190,.56);
  background:
    radial-gradient(circle at 50% 54%,rgba(138,73,255,.34),transparent 34%),
    radial-gradient(circle at 50% 72%,rgba(48,117,200,.13),transparent 48%),
    repeating-radial-gradient(circle at 50% 54%,rgba(167,139,250,.055) 0 1px,transparent 1px 25px),
    linear-gradient(180deg,#0b0822,#02020b);
}
.core::before {
  inset:9px;
  border-radius:11px;
  border:1px solid rgba(167,139,250,.12);
  box-shadow:inset 0 0 40px rgba(112,60,220,.12);
}
.core-stage { height:230px; }
.core-gem {
  width:110px;height:150px;
  filter:drop-shadow(0 0 12px rgba(103,232,249,.48)) drop-shadow(0 0 30px rgba(139,92,246,.7));
}
.core-gem::after { content:"FX"; }
.orbit { width:175px;height:175px; border-color:rgba(167,139,250,.36); box-shadow:0 0 25px rgba(124,58,237,.08); }
.orbit.slow { width:225px;height:225px; border-color:rgba(103,232,249,.18); }
.core-title { margin-bottom:8px; letter-spacing:.28em; }

/* Candidate + balance are framed like the reference lower altar row. */
.ls-mid { flex:0 0 154px; min-height:154px; gap:9px; }
.candidate,.balance { min-height:154px; padding:13px; }
.huge { font-size:clamp(27px,2.9vw,40px); text-shadow:0 0 18px rgba(182,108,255,.32); }
.side-gem { width:72px;height:100px; filter:drop-shadow(0 0 18px rgba(167,139,250,.62)); }
.scales { width:108px; filter:drop-shadow(0 0 13px rgba(212,175,90,.3)); }

/* Right rail: the reference has stacked economy/system cards. */
.ls-rail { gap:6px; overflow:hidden; }
.ls-rail .panel { padding:9px 10px; }
.round { flex:0 0 215px; padding:11px; background:radial-gradient(circle at 50% 10%,rgba(34,150,220,.09),transparent 46%),linear-gradient(180deg,#0a0a20,#04040e); }
.round-id { font-size:25px; }
.remain { font-size:22px; }
.rail-economy { flex:0 0 70px; }
.rail-system { flex:0 0 59px; }
.rail-economy strong,.rail-system strong { display:block; margin:3px 0 1px; font-family:var(--mono); font-size:16px; }
.rail-economy small,.rail-system small { font-size:7px; }
.purple-rail { border-color:rgba(182,108,255,.38); }
.purple-rail strong { color:#d8b4fe; text-shadow:0 0 13px rgba(182,108,255,.35); }
.ok-rail { border-color:rgba(97,226,148,.32); }
.ok-rail strong { color:var(--arcane-green); text-shadow:0 0 13px rgba(97,226,148,.30); }
.cyan-rail { border-color:rgba(56,189,248,.30); }
.cyan-rail strong { color:var(--arcane-blue); text-shadow:0 0 13px rgba(56,189,248,.25); }
.rail-system strong { color:#eee7ff; }
.bless { flex:1 1 auto; min-height:72px; border-color:rgba(74,222,128,.30); background:linear-gradient(135deg,rgba(11,39,31,.48),rgba(4,9,15,.98)); }
.bless strong { text-shadow:0 0 13px rgba(74,222,128,.35); }

/* Chronicles gets the ornate title and arcane confirmation pills. */
.history { flex:0 0 163px; min-height:163px; padding:9px 11px; }
.history-head { display:flex;align-items:center;justify-content:space-between;text-align:left;margin-bottom:5px; }
.history-title { display:flex;align-items:center;gap:9px; }
.history-sigil {
  width:27px;height:27px;display:grid;place-items:center;border:1px solid rgba(182,108,255,.45);border-radius:50%;
  color:#d8b4fe;box-shadow:0 0 16px rgba(182,108,255,.14);font-size:13px;
}
.history-head h2 { color:#e8ddfa;font-size:12px;letter-spacing:.15em; }
.history-head p { margin:2px 0 0;font-size:7px;letter-spacing:.08em; }
.history-head .count { position:static;font-size:7px; }
.tr { grid-template-columns:.72fr .8fr 1.25fr .68fr 2fr; gap:7px; padding:5px 3px; }
.tr.head { font-size:6px; color:#897da8; }
.history-row { display:grid;grid-template-columns:.72fr .8fr 1.25fr .68fr 2fr;gap:7px;padding:5px 3px;border-bottom:1px solid rgba(61,42,110,.4);font:8px var(--mono); }
.history-row > span { min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap; }
.validity {
  display:inline-block;padding:2px 6px;border-radius:999px;font-size:6px;letter-spacing:.06em;
  border:1px solid rgba(167,139,250,.32);background:rgba(124,58,237,.08);
}
.validity.valid { color:#7ee7a0;border-color:rgba(74,222,128,.28);background:rgba(74,222,128,.06); }
.validity.immature { color:#f3d77b;border-color:rgba(212,175,90,.28);background:rgba(212,175,90,.05); }
.validity.invalid { color:#ff858c;border-color:rgba(248,113,113,.32);background:rgba(248,113,113,.05); }

.footer { flex:0 0 18px; min-height:18px; padding:1px 3px; font-size:7px; letter-spacing:.08em; }

@keyframes dragonFloat { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-7px)} }
@media (prefers-reduced-motion:reduce){.dragon{animation:none}}

@media (max-width:1250px) {
  .ls-shell { grid-template-columns:132px minmax(0,1fr) 180px; }
  .ls-hero { grid-template-columns:105px minmax(0,1fr) 105px; }
  .dragon { width:108px; }
}

@media (max-width:1100px) {
  html,body { overflow:auto; }
  .ls-shell { grid-template-columns:1fr; height:auto; min-height:100dvh; overflow:visible; }
  .ls-side,.ls-rail { display:none; }
  .ls-main { height:auto; overflow:visible; }
  .ls-hero { flex:0 0 auto; min-height:210px; grid-template-columns:1fr; }
  .ls-hero-art { display:none; }
  .ls-forge { flex:none; min-height:560px; grid-template-columns:1fr; }
  .core { min-height:310px; }
  .ls-mid { flex:none; min-height:320px; grid-template-columns:1fr; }
  .history { flex:none; min-height:270px; }
}
'''
css_text = CSS.read_text(encoding='utf-8') if CSS.exists() else ''
css_marker = '/* ================================================================\n   ARCANE REFERENCE FINISH — visual-only layer'
if css_marker not in css_text:
    CSS.write_text(css_text.rstrip() + CSS_LAYER, encoding='utf-8')
    print('Arcane visual layer appended.')
else:
    print('Arcane visual layer already present.')

JS.write_text(r'''(() => {
  'use strict';
  if (window.__FIXEDCOIN_LIVESHARE_ARCANE__) return;
  window.__FIXEDCOIN_LIVESHARE_ARCANE__ = true;
  const $ = (id) => document.getElementById(id);
  const fix = (n) => (Number(n) || 0).toFixed(8) + ' FIX';
  const time = () => new Date().toLocaleTimeString([], {hour12:false});

  async function enrichArcaneRail() {
    try {
      const s = await fetch('/api/status?ts=' + Date.now(), {cache:'no-store'}).then(r => r.json());
      const w = s?.wallet || {};
      const confirmed = Number(w.confirmed) || 0;
      const pending = Number(w.unconfirmed ?? w.pending) || 0;
      const total = Number(w.total) || confirmed + pending + (Number(w.immature) || 0);
      if ($('railEstimated')) $('railEstimated').textContent = fix(total);
      if ($('railPending')) $('railPending').textContent = fix(pending);
      if ($('railPaid')) $('railPaid').textContent = fix(confirmed);
      if ($('railServerTime')) $('railServerTime').textContent = time();
    } catch (_) {
      if ($('railServerTime')) $('railServerTime').textContent = time();
    }
  }

  setInterval(enrichArcaneRail, 3000);
  enrichArcaneRail();
})();
''', encoding='utf-8')
print('Arcane rail JS written.')
