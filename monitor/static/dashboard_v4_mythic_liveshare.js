/* FIXEDCOIN LIVESHARE MYTHIC v1
 * Motion 13 mini + compositor-only DOM motes.
 * Reuses the same Motion runtime already used by magic_particles_v2.
 * No canvas, no rAF loop, no mining/API polling.
 */
(async()=>{
  'use strict';
  const reduced=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  if(reduced())return;

  const candidate=document.getElementById('candidate');
  const candidateCore=document.getElementById('candidateCore');
  const balanceGrid=document.querySelector('.balance-grid');
  if(!candidate||!candidateCore||!balanceGrid)return;

  let animate;
  try{
    ({animate}=await import('https://cdn.jsdelivr.net/npm/motion@13.1.1/mini/+esm'));
  }catch(_){
    // The visual CSS layer remains fully functional without Motion.
    return;
  }

  const coarse=window.matchMedia?.('(max-width:760px)').matches;
  const tiny=window.matchMedia?.('(max-width:620px)').matches;

  const makeMote=(host,x,y,kind='')=>{
    const el=document.createElement('i');
    el.className=`mythic-mote ${kind}`.trim();
    el.style.left=`${x}%`;
    el.style.top=`${y}%`;
    host.appendChild(el);
    return el;
  };

  // Candidate constellation: small, fixed-count DOM elements; Motion handles
  // transforms/opacity on the compositor instead of a canvas/rAF particle loop.
  const candidateLayer=document.createElement('div');
  candidateLayer.className='mythic-candidate-motes';
  candidateLayer.setAttribute('aria-hidden','true');
  candidate.appendChild(candidateLayer);

  const candidateSeed=[
    [18,24,'cyan'],[27,73,''],[35,18,'gold'],[44,82,''],[53,12,'star'],[61,76,'cyan'],
    [71,23,''],[79,66,'gold'],[87,38,'star'],[93,76,''],[14,57,''],[25,44,'bordeaux'],
    [39,63,'cyan'],[58,35,''],[68,54,'gold'],[83,16,''],[91,57,'cyan'],[49,92,'']
  ];
  const candidateMotes=candidateSeed.slice(0,coarse?12:(tiny?14:18)).map(([x,y,k])=>makeMote(candidateLayer,x,y,k));

  const runFloat=(el,i,scale=1)=>{
    const dx=(((i*17)%15)-7)*scale;
    const dy=(((i*29)%17)-8)*scale;
    const duration=4.8+(i%6)*.55;
    return animate(el,
      {transform:[`translate3d(0,0,0) scale(.55)`,`translate3d(${dx}px,${dy}px,0) scale(1.15)`,`translate3d(${-dx*.45}px,${-dy*.35}px,0) scale(.72)`,`translate3d(0,0,0) scale(.55)`],opacity:[.10,.88,.34,.10]},
      {duration,ease:'easeInOut',repeat:Infinity,delay:(i%9)*.14}
    );
  };
  const candidateAnimations=candidateMotes.map((el,i)=>runFloat(el,i,coarse?.7:1));

  // Treasury motes: only two per card, so even a 600 Hz mobile panel stays light.
  const balanceMotes=[];
  [...balanceGrid.querySelectorAll('.balance-card')].forEach((card,cardIndex)=>{
    const layer=document.createElement('div');
    layer.className='mythic-balance-motes';
    layer.setAttribute('aria-hidden','true');
    card.appendChild(layer);
    const count=coarse?1:2;
    for(let i=0;i<count;i++){
      const x=20+((cardIndex*31+i*43)%67);
      const y=24+((cardIndex*17+i*37)%52);
      const kind=(cardIndex===2?'gold':cardIndex===1||cardIndex===4?'cyan':'');
      balanceMotes.push(makeMote(layer,x,y,kind));
    }
  });
  const balanceAnimations=balanceMotes.map((el,i)=>runFloat(el,i+21,coarse?.45:.65));

  // One lightweight sweep across the candidate gate; no timer loop.
  const sweep=()=>animate(candidateCore,
    {filter:['brightness(1)','brightness(1.22)','brightness(1)']},
    {duration:1.4,ease:'easeInOut'}
  );
  sweep();

  const allAnimations=[...candidateAnimations,...balanceAnimations];
  document.addEventListener('visibilitychange',()=>{
    allAnimations.forEach(a=>{
      if(!a)return;
      if(document.hidden)a.pause?.();
      else a.play?.();
    });
  },{passive:true});

  // Mining events are already emitted by the existing realtime dashboard.
  // React only to those events; do not introduce another polling loop.
  window.addEventListener('fixedcoin:live',event=>{
    const type=event?.detail?.type;
    if(type!=='accept'&&type!=='block')return;
    sweep();
    candidateMotes.forEach((el,i)=>{
      const dx=(i%2?-1:1)*(6+(i%5)*2);
      const dy=(i%3-1)*(5+(i%4)*2);
      animate(el,
        {transform:[`translate3d(0,0,0) scale(.6)`,`translate3d(${dx}px,${dy}px,0) scale(1.65)`,`translate3d(0,0,0) scale(.6)`],opacity:[.08,1,.08]},
        {duration:type==='block'?.95:.62,ease:'easeOut'}
      );
    });
  },{passive:true});
})();
