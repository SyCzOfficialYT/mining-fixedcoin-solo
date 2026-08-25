#!/usr/bin/env python3
"""Apply the final FixedCoin cyberpunk HUD visual layer.

Idempotent: safe to run repeatedly in the Docker build pipeline.
"""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
CSS = Path('/app/monitor/static/dashboard_v4_reference_final.css')

html = HTML.read_text()
css = CSS.read_text()

if not re.search(r'class="[^\"]*\breference-dashboard\b[^\"]*"', html):
    raise RuntimeError('cyberpunk patch: reference dashboard anchor missing')

marker = '/* FIXCOIN CYBERPUNK POLISH v1 */'
if marker not in css:
    css += r'''

/* FIXCOIN CYBERPUNK POLISH v1 */
:root{
  --cp-cyan:#00eaff;
  --cp-cyan-soft:rgba(0,234,255,.28);
  --cp-green:#42ff7b;
  --cp-green-soft:rgba(66,255,123,.26);
  --cp-blue:#4aa8ff;
  --cp-ink:#01070b;
  --cp-grid:rgba(0,234,255,.055);
}
.reference-dashboard{
  position:relative!important;
  isolation:isolate;
  filter:saturate(1.08);
}
.reference-dashboard::before{
  content:"";
  position:fixed;
  inset:0;
  pointer-events:none;
  z-index:-1;
  background:
    linear-gradient(90deg,transparent 49.8%,rgba(0,234,255,.025) 50%,transparent 50.2%),
    linear-gradient(0deg,transparent 49.8%,rgba(66,255,123,.018) 50%,transparent 50.2%);
  background-size:120px 120px;
  mask-image:radial-gradient(circle at 50% 20%,black,transparent 82%);
}
.reference-dashboard::after{
  content:"";
  position:fixed;
  inset:0;
  pointer-events:none;
  z-index:999;
  opacity:.055;
  background:repeating-linear-gradient(0deg,rgba(255,255,255,.9) 0 1px,transparent 1px 4px);
  mix-blend-mode:screen;
  animation:cpScanlines 9s linear infinite;
}
.reference-dashboard .panel{
  position:relative;
  overflow:hidden;
  background:
    linear-gradient(135deg,rgba(2,14,21,.985),rgba(1,6,10,.985) 58%,rgba(2,18,20,.97))!important;
  box-shadow:
    inset 0 0 0 1px rgba(0,234,255,.035),
    inset 0 1px 0 rgba(255,255,255,.025),
    0 0 0 1px rgba(0,234,255,.055),
    0 24px 80px rgba(0,0,0,.55)!important;
}
.reference-dashboard .panel::before{
  content:"";
  position:absolute;
  left:0;right:0;top:0;height:1px;
  background:linear-gradient(90deg,transparent 0%,var(--cp-cyan) 18%,var(--cp-green) 50%,var(--cp-cyan) 82%,transparent 100%);
  opacity:.38;
  box-shadow:0 0 12px var(--cp-cyan-soft);
  animation:cpHudSweep 7s ease-in-out infinite;
  pointer-events:none;
}
.reference-dashboard .panel::after{
  content:"";
  position:absolute;
  inset:8px;
  border:1px solid rgba(0,234,255,.035);
  clip-path:polygon(0 0,18px 0,18px 1px,0 1px,0 18px,1px 18px,1px 0,100% 0,100% 18px,calc(100% - 1px) 18px,calc(100% - 1px) 1px,calc(100% - 18px) 1px,calc(100% - 18px) 0,100% 0,100% 100%,calc(100% - 18px) 100%,calc(100% - 18px) calc(100% - 1px),calc(100% - 1px) calc(100% - 1px),calc(100% - 1px) calc(100% - 18px),100% calc(100% - 18px),100% 100%,0 100%,0 calc(100% - 18px),1px calc(100% - 18px),1px calc(100% - 1px),18px calc(100% - 1px),18px 100%,0 100%);
  pointer-events:none;
  z-index:40;
}
.reference-dashboard .hero,
.reference-dashboard .candidate,
.reference-dashboard .block-history{
  box-shadow:
    inset 0 0 0 1px rgba(0,234,255,.055),
    inset 0 0 42px rgba(0,234,255,.018),
    0 0 28px rgba(0,234,255,.035),
    0 24px 80px rgba(0,0,0,.55)!important;
}
.reference-dashboard .eyebrow{
  text-shadow:0 0 10px rgba(0,234,255,.18);
}
.reference-dashboard .hero-value.best strong,
.reference-dashboard .candidate-pct{
  text-shadow:0 0 10px rgba(66,255,123,.22),0 0 28px rgba(66,255,123,.12);
}
.reference-dashboard .hero-value.network strong,
.reference-dashboard .round-id,
.reference-dashboard .remaining{
  text-shadow:0 0 10px rgba(0,234,255,.25),0 0 28px rgba(0,234,255,.12);
}
.reference-dashboard .target-track,
.reference-dashboard .candidate-track{
  background:linear-gradient(90deg,rgba(0,234,255,.035),rgba(0,234,255,.085),rgba(66,255,123,.04))!important;
  border-color:rgba(0,234,255,.24)!important;
  box-shadow:inset 0 0 14px rgba(0,0,0,.55),0 0 12px rgba(0,234,255,.05);
}
.reference-dashboard .target-track i,
.reference-dashboard .candidate-track i{
  box-shadow:0 0 8px var(--cp-green),0 0 22px var(--cp-green-soft)!important;
  animation:cpProgressPulse 1.65s ease-in-out infinite;
}
.reference-dashboard .target-track b{
  box-shadow:0 0 10px var(--cp-green),0 0 22px var(--cp-green-soft);
  animation:cpMarkerPulse 1.35s ease-in-out infinite;
}
.reference-dashboard .forge-stage{
  background:
    radial-gradient(circle at 50% 52%,rgba(66,255,123,.17),transparent 18%),
    radial-gradient(circle at 50% 52%,rgba(0,234,255,.13),transparent 43%),
    linear-gradient(180deg,#020a10 0%,#01070c 72%,#010408 100%)!important;
}
.reference-dashboard .forge-depth-grid{
  opacity:.62!important;
  animation:cpGridDrift 18s linear infinite;
}
.reference-dashboard .forge-center::before{
  content:"SYSTEM // HASH CORE // ONLINE";
  position:absolute;
  left:50%;
  top:calc(50% + 146px);
  transform:translateX(-50%);
  color:rgba(0,234,255,.38);
  font:700 7px/1 var(--rf-mono);
  letter-spacing:.28em;
  white-space:nowrap;
  text-shadow:0 0 10px rgba(0,234,255,.25);
  animation:cpTextFlicker 3.6s steps(1,end) infinite;
}
.reference-dashboard .core-logo{
  animation:cpCoreFloat 4.8s ease-in-out infinite;
}
.reference-dashboard .core-logo::before,
.reference-dashboard .core-logo::after{
  content:"";
  position:absolute;
  width:205px;height:205px;
  border:1px solid rgba(0,234,255,.12);
  clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%);
  transform:rotate(45deg);
  pointer-events:none;
}
.reference-dashboard .core-logo::before{animation:cpDiamond 12s linear infinite}
.reference-dashboard .core-logo::after{width:235px;height:235px;border-color:rgba(66,255,123,.08);animation:cpDiamond 17s linear reverse infinite}
.reference-dashboard .forge-metric,
.reference-dashboard .forge-counter,
.reference-dashboard .balance-card,
.reference-dashboard .stat{
  transition:border-color .25s ease,box-shadow .25s ease,transform .25s ease,background .25s ease;
}
.reference-dashboard .forge-metric:hover,
.reference-dashboard .forge-counter:hover,
.reference-dashboard .balance-card:hover,
.reference-dashboard .stat:hover{
  border-color:rgba(0,234,255,.42)!important;
  box-shadow:inset 0 0 0 1px rgba(0,234,255,.08),0 0 26px rgba(0,234,255,.08),0 20px 45px rgba(0,0,0,.65)!important;
}
.reference-dashboard .live i{
  box-shadow:0 0 8px var(--cp-green),0 0 18px var(--cp-green-soft)!important;
  animation:cpLivePulse 1.25s ease-in-out infinite;
}
.reference-dashboard .status.active,
.reference-dashboard .status.ok{
  box-shadow:0 0 10px rgba(66,255,123,.18);
  animation:cpLivePulse 2s ease-in-out infinite;
}
.reference-dashboard .history-count{
  box-shadow:inset 0 0 0 1px rgba(0,234,255,.04),0 0 14px rgba(0,234,255,.04);
}
.reference-dashboard .footer{
  border-top-color:rgba(0,234,255,.18)!important;
  box-shadow:0 -8px 28px rgba(0,234,255,.025);
}
@keyframes cpScanlines{from{transform:translateY(-2%)}to{transform:translateY(2%)}}
@keyframes cpHudSweep{0%,100%{opacity:.18;transform:scaleX(.7)}50%{opacity:.55;transform:scaleX(1)}}
@keyframes cpProgressPulse{0%,100%{filter:brightness(.9);opacity:.85}50%{filter:brightness(1.5);opacity:1}}
@keyframes cpMarkerPulse{0%,100%{transform:scaleY(.9);opacity:.72}50%{transform:scaleY(1.15);opacity:1}}
@keyframes cpGridDrift{from{background-position:0 0,0 0}to{background-position:0 46px,46px 0}}
@keyframes cpCoreFloat{0%,100%{transform:translateZ(100px) translateY(0)}50%{transform:translateZ(112px) translateY(-5px)}}
@keyframes cpDiamond{from{transform:rotate(45deg) scale(.92)}50%{transform:rotate(225deg) scale(1.04)}to{transform:rotate(405deg) scale(.92)}}
@keyframes cpLivePulse{0%,100%{opacity:.62;filter:brightness(.9)}50%{opacity:1;filter:brightness(1.45)}}
@keyframes cpTextFlicker{0%,96%,100%{opacity:.38}97%{opacity:.08}98%{opacity:.5}}
@media (max-width:760px){
  .reference-dashboard{width:calc(100% - 12px)!important;gap:9px!important}
  .reference-dashboard .panel{border-radius:12px!important}
  .reference-dashboard .forge-stage{height:500px!important;min-height:500px!important}
  .reference-dashboard .forge-side{width:125px!important;gap:12px!important;padding-top:24px!important}
  .reference-dashboard .left-side{left:12px!important}.reference-dashboard .right-side{right:12px!important}
  .reference-dashboard .forge-metric,.reference-dashboard .forge-counter{width:118px!important;min-width:118px!important;height:112px!important;min-height:112px!important;padding:11px!important}
  .reference-dashboard .forge-counter{height:102px!important;min-height:102px!important}
  .reference-dashboard .forge-metric>strong{font-size:17px!important}.reference-dashboard .forge-counter>strong{font-size:25px!important}
  .reference-dashboard .forge-metric svg{left:11px!important;right:11px!important;bottom:8px!important;width:calc(100% - 22px)!important;height:28px!important}
  .reference-dashboard .forge-center{left:135px!important;right:135px!important}
  .reference-dashboard .vardiff-badge{top:20px!important;min-width:125px!important;padding:9px 10px!important}.reference-dashboard .vardiff-badge strong{font-size:20px!important}
  .reference-dashboard .core-orbit{width:220px!important;height:220px!important}.reference-dashboard .core-orbit-b{width:275px!important;height:275px!important}.reference-dashboard .core-orbit-c{width:180px!important;height:180px!important}
  .reference-dashboard .core-logo{transform:translateZ(70px) scale(.76)!important}.reference-dashboard .core-logo::before{width:160px;height:160px}.reference-dashboard .core-logo::after{width:185px;height:185px}
  .reference-dashboard .forge-center::before{top:calc(50% + 122px)!important;font-size:5px!important;letter-spacing:.18em!important}
  .reference-dashboard .forge-bottom{left:12px!important;right:12px!important;bottom:14px!important}.reference-dashboard .combo{transform:translateZ(25px)!important}
  .reference-dashboard .forge-network-label{font-size:5px!important;letter-spacing:.12em!important}
  .reference-dashboard .balance-grid{grid-template-columns:repeat(2,1fr)!important}
  .reference-dashboard .balance-card:last-child{grid-column:1/-1}
}
@media (prefers-reduced-motion:reduce){
  .reference-dashboard::after,.reference-dashboard .panel::before,.reference-dashboard .forge-depth-grid,.reference-dashboard .core-logo,.reference-dashboard .core-logo::before,.reference-dashboard .core-logo::after,.reference-dashboard .target-track i,.reference-dashboard .candidate-track i,.reference-dashboard .target-track b,.reference-dashboard .live i{animation:none!important}
}
'''
    CSS.write_text(css)

# Bust the final reference CSS cache without touching the functional JS.
html = re.sub(r'(dashboard_v4_reference_final\.css\?v=)[^"\']+', r'\g<1>20260825-cp1', html)
HTML.write_text(html)
print('dashboard cyberpunk polish v1 applied')
