#!/usr/bin/env python3
# Install the LiveShare Arcane Reference presentation layer.
from pathlib import Path
import re

HTML = Path("/app/monitor/templates/dashboard_v4.html")
text = HTML.read_text(encoding="utf-8")
changed = False

css_link = '<link rel="stylesheet" href="/static/dashboard_v4_arcane_reference.css?v=20260828-arcane1">'
if css_link not in text:
    text = text.replace("</head>", css_link + "\n</head>", 1)
    changed = True

nav = r'''
<aside class="arcane-sidebar" aria-label="LiveShare navigation">
  <div class="arcane-brand">
    <div class="brand-sigil">✦</div>
    <strong>FIXEDCOIN</strong>
    <span>SOLO NODE</span>
  </div>
  <nav class="arcane-nav">
    <a class="active" href="#top" data-scroll>◈<span>Dashboard</span></a>
    <a href="#forge" data-scroll>◇<span>Mining</span></a>
    <a href="#forge" data-scroll>✦<span>Shares</span></a>
    <a href="#blockHistory" data-scroll>◆<span>Blocks</span></a>
    <a href="#forge" data-scroll>♙<span>Workers</span></a>
    <a href="#top" data-scroll>⚙<span>Settings</span></a>
    <a href="#blockHistory" data-scroll>≡<span>Logs</span></a>
    <a href="#top" data-scroll>○<span>System</span></a>
  </nav>
  <div class="arcane-node">
    <span>NODE STATUS</span>
    <b><i></i> ONLINE</b>
    <small>UPTIME <strong id="sidebarUptime">—</strong></small>
  </div>
</aside>
'''
if 'class="arcane-sidebar"' not in text:
    text = text.replace("<body>", "<body>\n" + nav, 1)
    changed = True

title_markup = r'''
<div class="arcane-hero-title">
  <span class="guardian guardian-left" aria-hidden="true"></span>
  <div class="title-rune">✦</div>
  <h1>LIVESHARE</h1>
  <p>SOLO MINING · MAGICAL NETWORK</p>
  <span class="guardian guardian-right" aria-hidden="true"></span>
</div>
<div class="arcane-stars" aria-hidden="true"></div>
'''
if 'class="arcane-hero-title"' not in text:
    needle = '      <p class="subtitle">Your best submitted work measured against the current FixedCoin network block target.</p>'
    text = text.replace(needle, needle + title_markup, 1)
    changed = True

workers_markup = '<div class="arcane-live-workers"><span>LIVE WORKERS</span><strong id="arcaneLiveWorkers">—</strong></div>'
if 'class="arcane-live-workers"' not in text:
    text = text.replace('<div class="core-title">LIVESHARE <span>· ARCANE CORE</span></div>', workers_markup + '<div class="core-title">LIVESHARE <span>· ARCANE CORE</span></div>', 1)
    changed = True

luck_markup = r'''
<div class="forge-metric glass-card parallax-card arcane-luck-card">
  <span>NETWORK LUCK</span><strong id="networkLuck">100.0%</strong><small>ROUND AVERAGE</small>
  <div class="luck-spark"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
</div>'''
if 'class="arcane-luck-card"' not in text:
    pattern = r'(<div class="forge-metric glass-card parallax-card"><span>SHARES / MIN</span>.*?</div>\s*)'
    text, n = re.subn(pattern, r'\1' + luck_markup, text, count=1, flags=re.S)
    if n:
        changed = True

balance_markup = r'''
<section class="reference-balance panel" aria-label="Arcane treasury">
  <div class="reference-balance-copy">
    <div class="section-heading"><span class="target-icon">◇</span><div><h2>ARCANE TREASURY</h2><p>Magical earnings · wallet state</p></div></div>
    <strong id="referenceBalance">—</strong>
    <span>FIXEDCOIN BALANCE</span>
    <small>LIVE CHAIN ECONOMY</small>
  </div>
  <div class="treasury-scales" aria-hidden="true"><div class="scale-beam"></div><div class="scale-pan left"></div><div class="scale-pan right"></div><div class="scale-chain left"></div><div class="scale-chain right"></div></div>
</section>
'''
if 'class="reference-balance panel"' not in text:
    needle = '  <section class="stats-grid stats-primary">'
    text = text.replace(needle, balance_markup + needle, 1)
    changed = True

rail = r'''
<aside class="arcane-rail" aria-label="LiveShare status ledger">
  <div class="rail-card violet"><span>ESTIMATED EARNINGS</span><strong id="railEstimated">0.00000000 FIX</strong><small>CHAIN REWARDS</small></div>
  <div class="rail-card green"><span>PENDING PAYOUT</span><strong id="railPending">0.00000000 FIX</strong><small>UNTRUSTED PENDING</small></div>
  <div class="rail-card cyan"><span>TOTAL PAID / REWARDS</span><strong id="railPaid">0.00000000 FIX</strong><small>RECORDED REWARDS</small></div>
  <div class="rail-card gold"><span>WORKERS ONLINE</span><strong id="railWorkers">—</strong><small>CONNECTED</small></div>
  <div class="rail-card blue"><span>NETWORK UPTIME</span><strong id="railUptime">—</strong><small>LIVE NODE</small></div>
  <div class="rail-card cyan"><span>SERVER TIME</span><strong id="railTime">—</strong><small>LOCAL NODE</small></div>
  <div class="rail-card blessing"><span>ARCANE BLESSING</span><strong>ACTIVE</strong><small>CHAIN SYNCHRONIZED</small><b>✦</b></div>
</aside>
'''
if 'class="arcane-rail"' not in text:
    text = text.replace("</main>", rail + "\n</main>", 1)
    changed = True

js = '<script defer src="/static/dashboard_v4_arcane_reference.js?v=20260828-arcane1"></script>'
if js not in text:
    text = text.replace("</body>", js + "\n</body>", 1)
    changed = True

if changed:
    HTML.write_text(text, encoding="utf-8")
    print("installed Arcane Reference presentation shell")
else:
    print("Arcane Reference presentation shell already installed")
