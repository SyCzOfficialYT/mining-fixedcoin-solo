/* FIXCOIN ARCANE MAGIC PARTICLES v3
 * Local Web Animations API. No CDN and no external dependency.
 */
(()=>{
  'use strict';
  const host=document.getElementById('fixMagicParticles');
  const core=document.getElementById('forgeCore');
  if(!host||!core)return;
  if(host.dataset.arcaneParticles==='v3')return;
  host.dataset.arcaneParticles='v3';

  const reduced=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const coarse=window.matchMedia?.('(max-width:620px)').matches;
  const seed=[[0,-82],[38,-68],[-44,-62],[68,-38],[-76,-20],[88,10],[-91,27],[64,52],[-62,58],[34,78],[-27,-86],[8,98],[101,-52],[-103,-48],[110,38],[-111,44],[49,101],[-50,92],[77,76],[-78,74],[0,-112],[0,114],[28,-108],[-31,108],[124,-10],[-126,8],[92,-92],[-94,94],[57,-118],[-60,118]];
  const count=coarse?18:30;
  const particles=[];
  for(let i=0;i<count;i++){
    const el=document.createElement('i');
    const p=seed[i]||[0,0];
    const x=p[0]*(coarse?.74:1),y=p[1]*(coarse?.74:1);
    el.className='fix-magic-particle'+(i%9===0?' cyan':'')+(i%13===0?' bordeaux':'')+(i%17===0?' amber':'')+(i%11===0?' spark':'');
    el.style.setProperty('--x',`${x}px`);el.style.setProperty('--y',`${y}px`);el.style.setProperty('--s',(.5+((i*17)%11)/11).toFixed(2));
    host.appendChild(el);particles.push({el,x,y,i});
  }
  const loops=particles.map(({el,x,y,i})=>{
    if(reduced())return null;
    const dx=((i*37)%35)-17,dy=((i*19)%31)-15;
    return el.animate(
      {transform:[`translate3d(${x}px,${y}px,0) scale(.45)`,`translate3d(${x+dx}px,${y+dy}px,0) scale(1.15)`,`translate3d(${x-dx*.45}px,${y-dy*.45}px,0) scale(.68)`,`translate3d(${x}px,${y}px,0) scale(.45)`],opacity:[.08,.95,.38,.08]},
      {duration:4200+(i%8)*520,easing:'ease-in-out',iterations:Infinity,delay:(i%10)*140}
    );
  });
  const burst=()=>{
    if(reduced())return;
    particles.forEach(({el,x,y})=>{
      el.animate({transform:[`translate3d(${x}px,${y}px,0) scale(.6)`,`translate3d(${x*1.24}px,${y*1.24}px,0) scale(1.7)`,`translate3d(${x}px,${y}px,0) scale(.6)`],opacity:[.1,1,.1]},{duration:760,easing:'cubic-bezier(.15,.8,.2,1)'});
    });
  };
  window.addEventListener('fixedcoin:live',e=>{const t=e?.detail?.type;if(t==='accept'||t==='block')burst()},{passive:true});
  core.addEventListener('pointerenter',burst,{passive:true});
  document.addEventListener('visibilitychange',()=>loops.forEach(a=>{if(!a)return;document.hidden?a.pause():a.play()}));
})();
