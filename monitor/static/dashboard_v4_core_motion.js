/* FIXCOIN CORE MOTION v4
 * Smooth Motion mini animation for the redesigned Prism Core.
 * No canvas, no requestAnimationFrame loop and no layout animation.
 */
(async()=>{
  'use strict';
  const core=document.getElementById('forgeCore');
  const mark=document.querySelector('.fix-core-mark');
  const glyph=document.querySelector('.fix-core-bolt');
  if(!core||!mark)return;
  mark.classList.add('motion-active');
  document.documentElement.dataset.fixedcoinCoreMotion='motion-prism-v4';
  let animate=null,idleAnimation=null,glyphAnimation=null,pulseAnimation=null;
  try{({animate}=await import('https://cdn.jsdelivr.net/npm/motion@13.1.1/mini/+esm'));}catch(_){return}
  const reduced=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  if(reduced())return;

  idleAnimation=animate(mark,{transform:['translate3d(0,0,0) scale(.988) rotate(-.10deg)','translate3d(0,-1.2px,0) scale(1.016) rotate(.10deg)','translate3d(0,0,0) scale(.988) rotate(-.10deg)']},{duration:6.8,ease:'easeInOut',repeat:Infinity});

  if(glyph){
    glyphAnimation=animate(glyph,{opacity:[.72,1,.78,.94,.72],transform:['scale(.985)','scale(1.035)','scale(1)','scale(1.018)','scale(.985)']},{duration:3.6,ease:'easeInOut',repeat:Infinity});
  }

  const pulse=()=>{
    if(reduced())return;
    pulseAnimation?.stop?.();
    pulseAnimation=animate(mark,{transform:['translate3d(0,0,0) scale(1)','translate3d(0,-2px,0) scale(1.055)','translate3d(0,0,0) scale(1)'],filter:['brightness(1)','brightness(1.28)','brightness(1)']},{duration:.62,ease:'easeOut'});
  };
  core.addEventListener('pointerenter',pulse,{passive:true});
  window.addEventListener('fixedcoin:live',e=>{const type=e?.detail?.type;if(type==='accept'||type==='block')pulse()},{passive:true});
  document.addEventListener('visibilitychange',()=>{if(document.hidden){idleAnimation?.pause?.();glyphAnimation?.pause?.()}else{idleAnimation?.play?.();glyphAnimation?.play?.()}});
})();
