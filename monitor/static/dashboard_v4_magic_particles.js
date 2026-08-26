/* FIXCOIN MAGIC PARTICLES v1
 * Uses Motion mini / Web Animations instead of a canvas or rAF loop.
 */
(async()=>{
  'use strict';
  const host=document.getElementById('fixMagicParticles');
  const core=document.getElementById('forgeCore');
  if(!host||!core)return;

  const reduced=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const coarse=window.matchMedia?.('(max-width:620px)').matches;
  const count=coarse?14:22;

  let animate;
  try{
    ({animate}=await import('https://cdn.jsdelivr.net/npm/motion@13.1.1/mini/+esm'));
  }catch(_){
    return;
  }
  if(reduced())return;

  const particles=[];
  const seed=[
    [0,-88],[42,-70],[-47,-63],[73,-35],[-78,-18],[91,12],[-94,28],
    [67,55],[-64,61],[35,83],[-28,-91],[8,101],[105,-58],[-108,-52],
    [116,42],[-116,45],[52,104],[-54,96],[82,80],[-82,78],[0,-118],[0,120]
  ];

  for(let i=0;i<count;i++){
    const el=document.createElement('i');
    el.className='fix-magic-particle'+(i%7===0?' cyan':'')+(i%11===0?' spark':'');
    const p=seed[i]||[0,0];
    const x=p[0]*(coarse?.78:1), y=p[1]*(coarse?.78:1);
    const scale=.55+((i*17)%9)/10;
    el.style.setProperty('--x',`${x}px`);
    el.style.setProperty('--y',`${y}px`);
    el.style.setProperty('--s',scale.toFixed(2));
    host.appendChild(el);
    particles.push({el,x,y,i});
  }

  const animateParticle=({el,x,y,i})=>{
    const dx=((i*37)%31)-15;
    const dy=((i*19)%27)-13;
    const drift=1.4+(i%5)*.28;
    const duration=4.8+(i%7)*.65;
    return animate(el,
      {
        transform:[
          `translate3d(${x}px,${y}px,0) scale(.65)`,
          `translate3d(${x+dx}px,${y+dy}px,0) scale(1)`,
          `translate3d(${x-dx*.55}px,${y-dy*.55}px,0) scale(.72)`,
          `translate3d(${x}px,${y}px,0) scale(.65)`
        ],
        opacity:[.18,.82,.48,.18]
      },
      {duration:duration*drift,ease:'easeInOut',repeat:Infinity,delay:(i%9)*.18}
    );
  };

  const animations=particles.map(animateParticle);

  const burst=()=>{
    particles.forEach(({el,x,y,i})=>{
      const dx=x*.16,dy=y*.16;
      animate(el,
        {transform:[`translate3d(${x}px,${y}px,0) scale(.7)`,`translate3d(${x+dx}px,${y+dy}px,0) scale(1.45)`,`translate3d(${x}px,${y}px,0) scale(.7)`],opacity:[.2,1,.2]},
        {duration:.7,ease:'easeOut'}
      );
    });
  };

  window.addEventListener('fixedcoin:live',e=>{
    const type=e?.detail?.type;
    if(type==='accept'||type==='block')burst();
  },{passive:true});

  document.addEventListener('visibilitychange',()=>{
    animations.forEach(a=>{
      if(document.hidden)a?.pause?.();
      else a?.play?.();
    });
  });
})();
