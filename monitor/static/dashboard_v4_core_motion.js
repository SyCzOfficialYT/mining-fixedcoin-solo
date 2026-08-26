/* FIXCOIN CORE MOTION v3
 * Smooth low-cost Motion mini animation for the FIX core.
 * No canvas, no requestAnimationFrame loop and no layout animation.
 * Continuous motion is compositor-friendly transform/opacity only.
 */
(async()=>{
  'use strict';

  const core=document.getElementById('forgeCore');
  const mark=document.querySelector('.fix-core-mark');
  const bolt=document.querySelector('.fix-core-bolt');
  if(!core||!mark)return;

  mark.classList.add('motion-active');
  document.documentElement.dataset.fixedcoinCoreMotion='motion-smooth-v3';

  let animate=null;
  let idleAnimation=null;
  let boltAnimation=null;
  let pulseAnimation=null;

  try{
    ({animate}=await import('https://cdn.jsdelivr.net/npm/motion@13.1.1/mini/+esm'));
  }catch(_){
    /* CSS ring motion remains active if Motion cannot be loaded. */
    return;
  }

  const reduced=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  if(reduced())return;

  /*
   * Very slow "breathing core".
   * The movement is intentionally tiny: it reads as alive without looking
   * like a permanently spinning game HUD and remains smooth on 60–600Hz.
   */
  idleAnimation=animate(mark,
    {transform:[
      'translate3d(0,0,0) scale(.992) rotate(-0.08deg)',
      'translate3d(0,-1px,0) scale(1.012) rotate(0.08deg)',
      'translate3d(0,0,0) scale(.992) rotate(-0.08deg)'
    ]},
    {duration:7.5,ease:'easeInOut',repeat:Infinity}
  );

  /* The FIX bolt gets a separate opacity-only shimmer. */
  if(bolt){
    boltAnimation=animate(bolt,
      {opacity:[.78,1,.78]},
      {duration:3.2,ease:'easeInOut',repeat:Infinity}
    );
  }

  const pulse=()=>{
    if(reduced())return;
    pulseAnimation?.stop?.();
    pulseAnimation=animate(mark,
      {transform:[
        'translate3d(0,0,0) scale(1)',
        'translate3d(0,-1.5px,0) scale(1.045)',
        'translate3d(0,0,0) scale(1)'
      ],opacity:[1,1,1]},
      {duration:.58,ease:'easeOut'}
    );
  };

  core.addEventListener('pointerenter',pulse,{passive:true});
  window.addEventListener('fixedcoin:live',e=>{
    const type=e?.detail?.type;
    if(type==='accept'||type==='block')pulse();
  },{passive:true});

  document.addEventListener('visibilitychange',()=>{
    if(document.hidden){
      idleAnimation?.pause?.();
      boltAnimation?.pause?.();
    }else{
      idleAnimation?.play?.();
      boltAnimation?.play?.();
    }
  });
})();
