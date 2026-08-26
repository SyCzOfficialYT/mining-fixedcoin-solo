/* FIXCOIN MAGIC PARTICLES v2
 * Motion mini / Web Animations. More visible, still no canvas/rAF particle loop.
 */
(async()=>{
  'use strict';
  const host=document.getElementById('fixMagicParticles');
  if(!host)return;
  const reduced=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  if(reduced())return;
  const coarse=window.matchMedia?.('(max-width:760px)').matches;
  const count=coarse?20:34;
  let animate;
  try{({animate}=await import('https://cdn.jsdelivr.net/npm/motion@13.1.1/mini/+esm'));}catch(_){return}
  const seed=[[0,-92],[38,-84],[-42,-78],[72,-58],[-78,-48],[102,-22],[-106,-8],[118,18],[-118,28],[94,54],[-92,62],[58,82],[-55,88],[22,108],[-20,-112],[8,122],[135,-48],[-136,-44],[145,44],[-144,54],[78,112],[-76,108],[42,128],[-45,-124],[158,-4],[-158,12],[0,-145],[0,145],[112,86],[-112,92],[126,-86],[-126,-80],[176,0],[-176,0]];
  const particles=[];
  for(let i=0;i<count;i++){
    const el=document.createElement('i');
    el.className='fix-magic-particle'+(i%9===0?' cyan':'')+(i%17===0?' amber':'')+(i%8===0?' spark':'');
    const p=seed[i]||[0,0],x=p[0]*(coarse?.74:1),y=p[1]*(coarse?.74:1),s=.55+((i*13)%8)/10;
    el.style.setProperty('--x',`${x}px`);el.style.setProperty('--y',`${y}px`);el.style.setProperty('--s',s.toFixed(2));
    host.appendChild(el);particles.push({el,x,y,i});
  }
  const animations=particles.map(({el,x,y,i})=>{
    const dx=((i*29)%25)-12,dy=((i*17)%23)-11,duration=5.2+(i%6)*.55;
    return animate(el,{transform:[`translate3d(${x}px,${y}px,0) scale(.55)`,`translate3d(${x+dx}px,${y+dy}px,0) scale(1.08)`,`translate3d(${x-dx*.5}px,${y-dy*.5}px,0) scale(.72)`,`translate3d(${x}px,${y}px,0) scale(.55)`],opacity:[.12,.92,.42,.12]},{duration,ease:'easeInOut',repeat:Infinity,delay:(i%11)*.12});
  });
  const burst=()=>particles.forEach(({el,x,y})=>{const dx=x*.12,dy=y*.12;animate(el,{transform:[`translate3d(${x}px,${y}px,0) scale(.6)`,`translate3d(${x+dx}px,${y+dy}px,0) scale(1.6)`,`translate3d(${x}px,${y}px,0) scale(.6)`],opacity:[.12,1,.12]},{duration:.72,ease:'easeOut'});});
  window.addEventListener('fixedcoin:live',e=>{const t=e?.detail?.type;if(t==='accept'||t==='block')burst()},{passive:true});
  document.addEventListener('visibilitychange',()=>animations.forEach(a=>document.hidden?a?.pause?.():a?.play?.()),{passive:true});
})();
