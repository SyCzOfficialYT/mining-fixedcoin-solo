/* FIXCOIN CORE MOTION v1
 * Motion mini is intentionally used instead of a canvas/rAF particle renderer.
 * The animation is compositor-friendly and follows the display's native refresh cadence.
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

  document.addEventListener('visibilitychange',()=>{
    if(!idleAnimation)return;
    if(document.hidden) idleAnimation.pause();
    else idleAnimation.play();
  });

  /* Reuse the existing SSE stream for a very small, event-driven core reaction.
     No polling and no animation loop are added here. */
  try{
    const es=new EventSource('/api/stream');
    es.onmessage=e=>{
      try{
        const d=JSON.parse(e.data||'{}');
        if(d.type==='accept'||d.type==='block')pulse();
      }catch(_){ }
    };
  }catch(_){ }
})();
