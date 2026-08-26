/* FIXCOIN ARCANE CORE MOTION v5
 * Local-only motion. No CDN, no external runtime dependency.
 * Continuous prism/orbit motion + live share/block pulses.
 */
(()=>{
  'use strict';
  const core=document.getElementById('forgeCore');
  const mark=document.querySelector('.fix-core-mark');
  if(!core||!mark)return;
  if(document.documentElement.dataset.fixedcoinCoreMotion==='arcane-v5')return;
  document.documentElement.dataset.fixedcoinCoreMotion='arcane-v5';

  const style=document.createElement('style');
  style.textContent=`
    .fix-core-mark{transform-box:fill-box;transform-origin:center;will-change:transform,filter}
    .fix-core-mark.motion-active{animation:fxCoreFloat 6.4s ease-in-out infinite,fxCoreGlow 3.2s ease-in-out infinite}
    .fix-core-ring.r1{animation:fxRingA 18s linear infinite;transform-origin:80px 80px}
    .fix-core-ring.r2{animation:fxRingB 11s linear infinite;transform-origin:80px 80px}
    .fix-core-ring.r3{animation:fxRingA 7s linear infinite reverse;transform-origin:80px 80px}
    .fix-core-grid{animation:fxGrid 2.8s ease-in-out infinite}
    .fix-core-node{animation:fxNode 1.15s ease-in-out infinite}
    .fix-core-scanline{animation:fxScan 2.1s linear infinite}
    .fix-core-ray{animation:fxRay 3.6s ease-in-out infinite}
    #forgeCore::after{content:"";position:absolute;inset:8%;border-radius:50%;pointer-events:none;background:radial-gradient(circle,rgba(150,90,255,.18),transparent 52%);filter:blur(12px);animation:fxAura 2.8s ease-in-out infinite}
    #forgeCore.fx-live-pulse{animation:fxCoreHit .72s cubic-bezier(.2,.9,.2,1) both}
    #forgeCore.fx-block-pulse{animation:fxBlock 1.35s cubic-bezier(.15,.8,.2,1) both}
    @keyframes fxCoreFloat{0%,100%{transform:translate3d(0,0,0) rotate(-.6deg) scale(.985)}50%{transform:translate3d(0,-5px,0) rotate(.6deg) scale(1.018)}}
    @keyframes fxCoreGlow{0%,100%{filter:brightness(1) drop-shadow(0 0 12px rgba(100,80,255,.25))}50%{filter:brightness(1.18) drop-shadow(0 0 30px rgba(80,220,255,.55))}}
    @keyframes fxRingA{to{transform:rotate(360deg)}}
    @keyframes fxRingB{to{transform:rotate(-360deg)}}
    @keyframes fxGrid{0%,100%{opacity:.48}50%{opacity:1;filter:drop-shadow(0 0 5px rgba(90,220,255,.8))}}
    @keyframes fxNode{0%,100%{r:3;opacity:.7}50%{r:6;opacity:1}}
    @keyframes fxScan{0%{opacity:.15;transform:translateX(-8px)}50%{opacity:1}100%{opacity:.15;transform:translateX(8px)}}
    @keyframes fxRay{0%,100%{opacity:.35}50%{opacity:1;filter:drop-shadow(0 0 7px rgba(170,100,255,.9))}}
    @keyframes fxAura{0%,100%{opacity:.35;transform:scale(.85)}50%{opacity:.9;transform:scale(1.08)}}
    @keyframes fxCoreHit{0%{transform:scale(1);filter:brightness(1)}25%{transform:scale(1.1) translateY(-4px);filter:brightness(1.7) drop-shadow(0 0 42px rgba(80,240,255,.9))}100%{transform:scale(1);filter:brightness(1)}}
    @keyframes fxBlock{0%{transform:scale(1)}20%{transform:scale(1.16);filter:brightness(2) drop-shadow(0 0 65px rgba(255,210,80,1))}45%{transform:scale(.96)}70%{transform:scale(1.08);filter:brightness(1.45) drop-shadow(0 0 45px rgba(80,255,160,.9))}100%{transform:scale(1)}}
    @media(prefers-reduced-motion:reduce){.fix-core-mark.motion-active,.fix-core-ring,.fix-core-grid,.fix-core-node,.fix-core-scanline,.fix-core-ray,#forgeCore::after{animation:none!important}}
  `;
  document.head.appendChild(style);
  mark.classList.add('motion-active');

  const reduced=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const pulse=(block=false)=>{
    if(reduced())return;
    core.classList.remove('fx-live-pulse','fx-block-pulse');
    void core.offsetWidth;
    core.classList.add(block?'fx-block-pulse':'fx-live-pulse');
    setTimeout(()=>core.classList.remove('fx-live-pulse','fx-block-pulse'),1500);
  };

  let lastAccepted=null,lastHeight=null,lastBest=null;
  const sync=async()=>{
    try{
      const r=await fetch('/api/status',{cache:'no-store'});
      if(!r.ok)return;
      const d=await r.json();
      const accepted=Number(d?.mining?.accepted??d?.round?.shares??0);
      const height=Number(d?.round?.height??d?.node?.height??0);
      const best=Number(d?.mining?.best_share??d?.round?.best_share??0);
      if(lastAccepted!==null&&accepted>lastAccepted)pulse(false);
      if(lastHeight!==null&&height>lastHeight)pulse(true);
      if(lastBest!==null&&best>lastBest*1.08)pulse(false);
      lastAccepted=accepted;lastHeight=height;lastBest=best;
    }catch(_){/* dashboard remains animated offline */}
  };
  core.addEventListener('pointerenter',()=>pulse(false),{passive:true});
  sync();
  setInterval(sync,5000);
})();
