/* FIXCOIN CORE MOTION v2
 * Motion mini replaces the old canvas/rAF particle renderer.
 * Only transform/opacity are animated, so the browser can synchronize the
 * motion to the display's native refresh cadence (60/90/120/144/165/240/360/600Hz).
 */
(async()=>{
  'use strict';
  const core=document.getElementById('forgeCore');
  const mark=document.querySelector('.fix-core-mark');
  if(!core||!mark)return;

  mark.classList.add('motion-active');
  document.documentElement.dataset.fixedcoinCoreMotion='motion-mini';

  let animate=null;
  let idleAnimation=null;
  let pulseAnimation=null;

  try{
    ({animate}=await import('https://cdn.jsdelivr.net/npm/motion@13.1.1/mini/+esm'));
  }catch(_){
    /* CSS ring animation remains active if the CDN is unavailable. */
    return;
  }

  const reduced=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  if(reduced())return;

  idleAnimation=animate(mark,
    {transform:[
      'translate3d(0,0,0) scale(0.985) rotate(-0.25deg)',
      'translate3d(0,-1.5px,0) scale(1.01) rotate(0.25deg)',
      'translate3d(0,0,0) scale(0.985) rotate(-0.25deg)'
    ]},
    {duration:5.6,ease:'easeInOut',repeat:Infinity}
  );

  const pulse=()=>{
    if(!idleAnimation||reduced())return;
    pulseAnimation?.stop?.();
    pulseAnimation=animate(mark,
      {transform:[
        'translate3d(0,0,0) scale(1)',
        'translate3d(0,-2px,0) scale(1.055)',
        'translate3d(0,0,0) scale(1)'
      ],opacity:[1,.98,1]},
      {duration:.72,ease:'easeOut'}
    );
  };

  core.addEventListener('pointerenter',pulse,{passive:true});
  window.addEventListener('fixedcoin:live',e=>{
    const type=e?.detail?.type;
    if(type==='accept'||type==='block')pulse();
  },{passive:true});

  document.addEventListener('visibilitychange',()=>{
    if(!idleAnimation)return;
    if(document.hidden) idleAnimation.pause();
    else idleAnimation.play();
  });
})();
