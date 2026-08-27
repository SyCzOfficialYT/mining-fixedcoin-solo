#!/usr/bin/env python3
"""Apply the final Liveshare composition/layout without touching dashboard data logic.

The base Liveshare dashboard already owns the markup and data bindings. This patch
only appends a deterministic layout layer so the visual composition matches the
reference: framed left navigation, wide central forge, candidate/balance row,
chronicles, and a compact right status rail.
"""
from pathlib import Path

CSS = r'''
/* === LIVESHARE REFERENCE LAYOUT — FINAL COMPOSITION === */
:root {
  --ls-sidebar: 148px;
  --ls-rail: 198px;
  --ls-gap: 8px;
}

html, body { width:100%; min-height:100%; overflow:hidden; }
body { background:#04030d; }

.ls-shell {
  width:100vw;
  height:100dvh;
  min-height:0;
  padding:6px;
  gap:var(--ls-gap);
  grid-template-columns:var(--ls-sidebar) minmax(0,1fr) var(--ls-rail);
  overflow:hidden;
  background:
    radial-gradient(ellipse at 50% -15%, rgba(109,40,217,.30), transparent 42%),
    radial-gradient(ellipse at 100% 45%, rgba(30,120,180,.10), transparent 30%),
    radial-gradient(ellipse at 0% 85%, rgba(80,30,150,.12), transparent 30%),
    #04030d;
}

.ls-side {
  min-height:0;
  padding:10px 8px;
  gap:8px;
  border-radius:12px;
  background:linear-gradient(180deg,rgba(10,8,27,.98),rgba(4,3,14,.98));
  border-color:rgba(167,139,250,.24);
  box-shadow:inset -1px 0 rgba(212,175,90,.08),0 0 30px rgba(0,0,0,.45);
}

.ls-brand { gap:7px; padding:2px 3px 8px; border-bottom:1px solid rgba(212,175,90,.16); }
.ls-brand svg { width:32px; height:32px; }
.ls-brand strong { font-size:10px; letter-spacing:.13em; }
.ls-brand span { font-size:8px; letter-spacing:.12em; }
.ls-side nav { gap:2px; }
.ls-side nav button {
  min-height:35px;
  padding:7px 8px;
  border-radius:7px;
  font-size:9px;
  letter-spacing:.10em;
}
.ls-side-gem { min-height:74px; }
.ls-side-gem .gem { width:52px; height:70px; }
.ls-node { font-size:9px; gap:3px; padding-top:8px; }
.ls-node .ls-label { font-size:7px; }

.ls-main {
  min-height:0;
  height:100%;
  gap:var(--ls-gap);
  overflow:hidden;
}

.panel, .card {
  border-radius:10px;
  border-color:rgba(111,82,170,.48);
  background:linear-gradient(180deg,rgba(10,9,27,.91),rgba(4,4,16,.96));
  box-shadow:inset 0 0 0 1px rgba(167,139,250,.035),0 8px 24px rgba(0,0,0,.34);
}

.ls-hero {
  flex:0 0 184px;
  min-height:184px;
  grid-template-columns:118px minmax(0,1fr) 118px;
  border-radius:10px;
  border-color:rgba(212,175,90,.28);
}
.ls-hero-art { overflow:hidden; }
.dragon { width:112px; height:170px; opacity:.94; }
.hero-gem { bottom:5px; width:48px; height:65px; }
.ls-hero-center { padding:8px 6px 10px; }
.kicker { font-size:8px; letter-spacing:.24em; }
.ls-hero-center h1 {
  margin:2px 0 9px;
  font-size:clamp(24px,2.8vw,40px);
  letter-spacing:.30em;
  text-shadow:0 0 26px rgba(167,139,250,.65);
}
.versus { grid-template-columns:minmax(0,1fr) 58px minmax(0,1fr); gap:6px; }
.stat strong { font-size:clamp(20px,2.25vw,31px); }
.stat small,.bar-cap,.stat em { font-size:8px; }
.compass { width:54px; height:54px; }
.bar { height:6px; margin-top:6px; }

.ls-forge {
  flex:1 1 auto;
  min-height:0;
  grid-template-columns:minmax(165px,.82fr) minmax(230px,1.28fr) minmax(165px,.82fr);
  gap:8px;
  padding:8px;
}
.ls-forge .col { min-height:0; gap:8px; }
.ls-forge .card { min-height:0; padding:9px 11px; }
.ls-forge .card strong { font-size:20px; margin:4px 0 1px; }
.ls-forge .card small { font-size:8px; }
.ls-forge .spark { height:22px; margin-top:5px; }
.core {
  min-height:0;
  border-radius:12px;
  background:
    radial-gradient(circle at 50% 55%,rgba(124,58,237,.33),transparent 42%),
    radial-gradient(circle at 50% 100%,rgba(67,56,202,.12),transparent 48%),
    linear-gradient(180deg,#0a0820,#03030e);
}
.core > .ls-label { margin-top:3px; font-size:8px; }
.core > strong { font-size:20px; }
.core-stage { height:100%; min-height:130px; }
.core-gem { width:96px; height:130px; }
.orbit { width:142px; height:142px; }
.orbit.slow { width:188px; height:188px; }
.core-title { margin-bottom:7px; font-size:8px; }

.ls-mid {
  flex:0 0 142px;
  min-height:142px;
  grid-template-columns:1.12fr 1fr;
  gap:8px;
}
.candidate,.balance { min-height:0; padding:12px; grid-template-columns:minmax(0,1fr) 88px; }
.sub { font-size:9px; margin:3px 0 6px; }
.huge { font-size:clamp(24px,2.7vw,36px); }
.caption { font-size:8px; margin-top:4px; }
.next { margin-top:8px; font-size:9px; }
.side-gem { width:66px; height:90px; }
.scales { width:88px; }
.liveshare-tag { font-size:8px; margin:4px 0; }
.bal-grid { gap:4px; margin-top:5px; }
.bal-grid span { font-size:8px; }
.bal-grid b { font-size:9px; }

.stats-row { display:none; }

.history {
  flex:0 0 142px;
  min-height:142px;
  padding:9px 11px;
  overflow:hidden;
}
.history-head { margin-bottom:4px; }
.history-head h2 { font-size:11px; letter-spacing:.16em; }
.history-head p { font-size:8px; margin-top:2px; }
.history-head .count { font-size:7px; padding:3px 6px; }
.table { font-size:8px; }
.tr { grid-template-columns:.72fr .85fr 1fr .62fr 1.9fr; gap:6px; padding:5px 3px; }
.tr.head { font-size:7px; }
.empty { padding:8px; }

.footer {
  flex:0 0 20px;
  min-height:20px;
  padding:2px 4px;
  gap:8px;
  font-size:7px;
}

.ls-rail {
  min-height:0;
  max-height:none;
  height:100%;
  overflow:hidden;
  gap:6px;
}
.ls-rail .panel { flex:0 0 auto; }
.round { padding:10px; }
.round-id { font-size:20px; margin:4px 0 7px; }
.remain { font-size:21px; }
.badge { font-size:8px; margin-top:4px; padding:2px 7px; }
.ls-rail .card { padding:9px 10px; }
.ls-rail .card strong { font-size:17px; margin:3px 0 1px; }
.ls-rail .card small { font-size:7px; }
.bless { padding:9px; gap:7px; }

/* Keep the magical palette, but make the reference hierarchy obvious. */
.ls-rail .gold strong { color:var(--gold-soft); }
.ls-rail .ok strong { color:var(--ok); }
.ls-rail .bad strong { color:var(--bad); }

@media (max-width:1250px) {
  :root { --ls-sidebar:132px; --ls-rail:174px; }
  .ls-hero { grid-template-columns:90px minmax(0,1fr) 90px; }
  .dragon { width:92px; }
  .ls-forge { grid-template-columns:minmax(140px,.78fr) minmax(200px,1.15fr) minmax(140px,.78fr); }
}

@media (max-width:980px) {
  html,body { overflow:auto; }
  .ls-shell { height:auto; min-height:100dvh; grid-template-columns:1fr; overflow:visible; }
  .ls-side,.ls-rail { display:none; }
  .ls-main { height:auto; overflow:visible; }
  .ls-hero { flex:0 0 auto; min-height:180px; grid-template-columns:1fr; }
  .ls-hero-art { display:none; }
  .ls-forge { flex:none; min-height:520px; grid-template-columns:1fr; }
  .core { min-height:280px; }
  .ls-mid { flex:none; min-height:300px; grid-template-columns:1fr; }
  .history { flex:none; min-height:260px; }
  .footer { flex:none; }
}
'''

path = Path('/app/monitor/static/dashboard_liveshare.css')
text = path.read_text(encoding='utf-8') if path.exists() else ''
marker = '/* === LIVESHARE REFERENCE LAYOUT — FINAL COMPOSITION === */'
if marker not in text:
    path.write_text(text.rstrip() + '\n\n' + CSS.lstrip(), encoding='utf-8')
    print('Liveshare reference layout applied.')
else:
    print('Liveshare reference layout already applied.')
