/* FIXCOIN FX CORE MOTION v1
 * Motion mini / native WAAPI: layered, low-cost "living core" animation.
 */
(async()=>{
  'use strict';
  const mark=document.querySelector('.fix-core-mark');
  const glyph=document.querySelector('.fix-core-glyph');
  const accent=document.querySelector('.fix-core-glyph-secondary');
  if(!mark||!glyph)return;
  const reduced=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  if(reduced())return;
  let animate;
  try{({animate}=await import('https://cdn.jsdelivr.net/npm/motion@13.1.1/mini/+esm'));}catch(_){return}

  const mobile=window.matchMedia?.('(max-width:760px)').matches;
  const scale=mobile?.88:1;
  const animations=[];

  const coreFloat=animate(mark,{transform:[`translate3d(0,0,0) scale(${.985*scale})`,`translate3d(0,-2px,0) scale(${1.015*scale})`,`translate3d(0,0,0) scale(${.985*scale})`],opacity:[.96,1,.96]},{duration:5.8,ease:'easeInOut',repeat:Infinity});
  animations.push(coreFloat);

  const glyphSpin=animate(glyph,{transform:['rotate(0deg) scale(.96)','rotate(7deg) scale(1.04)','rotate(-4deg) scale(1)','rotate(0deg) scale(.96)'],opacity:[.76,1,.86,.76]},{duration:4.6,ease:'easeInOut',repeat:Infinity});
  animations.push(glyphSpin);

  if(accent){
    animations.push(animate(accent,{transform:['rotate(0deg) scale(.86)','rotate(-180deg) scale(1.08)','rotate(-360deg) scale(.86)'],opacity:[.35,.9,.35]},{duration:11,ease:'linear',repeat:Infinity}));
  }

  const pulse=()=>{
    if(reduced())return;
    animate(glyph,{transform:['scale(1)','scale(1.22)','scale(1)'],opacity:[.8,1,.8]},{duration:.62,ease:'easeOut'});
    if(accent)animate(accent,{opacity:[.3,1,.3]},{duration:.62,ease:'easeOut'});
  };
  window.addEventListener('fixedcoin:live',e=>{const t=e?.detail?.type;if(t==='accept'||t==='block')pulse()},{passive:true});
  document.addEventListener('visibilitychange',()=>{animations.forEach(a=>document.hidden?a?.pause?.():a?.play?.())},{passive:true});
})();
