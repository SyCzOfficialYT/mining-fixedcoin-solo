/* FIXCOIN MAGIC PARTICLES v2
 * Motion mini / Web Animations. DOM only: no canvas and no rAF particle loop.
 */
(async()=>{
  'use strict';
  const host=document.getElementById('fixMagicParticles');
  const core=document.getElementById('forgeCore');
  if(!host||!core)return;
  const reduced=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const coarse=window.matchMedia?.('(max-width:620px)').matches;
  const count=coarse?18:30;
  let animate;
  try{({animate}=await import('https://cdn.jsdelivr.net/npm/motion@13.1.1/mini/+esm'));}catch(_){return}
  if(reduced())return;

  const seed=[
    [0,-82],[38,-68],[-44,-62],[68,-38],[-76,-20],[88,10],[-91,27],[64,52],[-62,58],
    [34,78],[-27,-86],[8,98],[101,-52],[-103,-48],[110,38],[-111,44],[49,101],[-50,92],
    [77,76],[-78,74],[0,-112],[0,114],[28,-108],[-31,108],[124,-10],[-126,8],[92,-92],[-94,94],
    [57,-118],[-60,118]
  ];
  const particles=[];
  for(let i=0;i<count;i++){
    const el=document.createElement('i');
    const cls=i%9===0?' cyan':i%13===0?' bordeaux':i%17===0?' amber':'';
    el.className='fix-magic-particle'+cls+(i%11===0?' spark':'');
    const p=seed[i]||[0,0];
    const x=p[0]*(coarse?.74:1),y=p[1]*(coarse?.74:1);
    const scale=.5+((i*17)%11)/11;
    el.style.setProperty('--x',`${x}px`);el.style.setProperty('--y',`${y}px`);el.style.setProperty('--s',scale.toFixed(2));
    host.appendChild(el);particles.push({el,x,y,i});
  }
  const animateParticle=({el,x,y,i})=>{
    const dx=((i*37)%35)-17,dy=((i*19)%31)-15;
    const duration=4.2+(i%8)*.52;
    return animate(el,{transform:[`translate3d(${x}px,${y}px,0) scale(.55)`,`translate3d(${x+dx}px,${y+dy}px,0) scale(1.12)`,`translate3d(${x-dx*.45}px,${y-dy*.45}px,0) scale(.68)`,`translate3d(${x}px,${y}px,0) scale(.55)`],opacity:[.12,.88,.42,.12]},{duration,ease:'easeInOut',repeat:Infinity,delay:(i%10)*.14});
  };
  const animations=particles.map(animateParticle);
  const burst=()=>particles.forEach(({el,x,y,i})=>{const dx=x*.18,dy=y*.18;animate(el,{transform:[`translate3d(${x}px,${y}px,0) scale(.65)`,`translate3d(${x+dx}px,${y+dy}px,0) scale(1.55)`,`translate3d(${x}px,${y}px,0) scale(.65)`],opacity:[.15,1,.15]},{duration:.72,ease:'easeOut'})});
  window.addEventListener('fixedcoin:live',e=>{const type=e?.detail?.type;if(type==='accept'||type==='block')burst()},{passive:true});
  core.addEventListener('pointerenter',burst,{passive:true});
  document.addEventListener('visibilitychange',()=>animations.forEach(a=>document.hidden?a?.pause?.():a?.play?.()));
})();
