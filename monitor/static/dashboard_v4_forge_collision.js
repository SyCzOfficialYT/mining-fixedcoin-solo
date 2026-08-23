(()=>{
'use strict';
if(window.__FIXEDCOIN_FORGE_COLLISION_V7__) return;
window.__FIXEDCOIN_FORGE_COLLISION_V7__=true;
const forge=document.getElementById('forge');
const stage=document.getElementById('forgeStage');
const core=document.getElementById('forgeCore');
const accepted=document.getElementById('acceptedCount');
const rejected=document.getElementById('rejectedCount');
if(!forge||!stage||!core||!accepted||!rejected)return;
const center=el=>{const r=el.getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2}};
const local=p=>{const r=stage.getBoundingClientRect();return{x:p.x-r.left,y:p.y-r.top}};
const source=()=>local(center(core));
const target=kind=>{const el=stage.querySelector(kind==='accept'?'.forge-counter.accepted':'.forge-counter.rejected');return el?local(center(el)):source()};
const bezier=(a,c,b,t)=>{const u=1-t;return{x:u*u*a.x+2*u*t*c.x+t*t*b.x,y:u*u*a.y+2*u*t*c.y+t*t*b.y}};
let layer=stage.querySelector('.collision-field');
if(!layer){layer=document.createElement('div');layer.className='collision-field';layer.setAttribute('aria-hidden','true');stage.appendChild(layer)}

/* Per-particle neon: a hard, short strobe with a real dark interval. */
const pulseState={accept:{busy:false,queue:0},reject:{busy:false,queue:0}};
function pulseCounter(kind){
  const card=stage.querySelector(kind==='accept'?'.forge-counter.accepted':'.forge-counter.rejected');
  if(!card)return;
  pulseState[kind].queue++;
  if(pulseState[kind].busy)return;
  pulseState[kind].busy=true;
  const step=()=>{
    if(pulseState[kind].queue<=0){pulseState[kind].busy=false;return}
    pulseState[kind].queue--;
    const id=String(Number(card.dataset.collisionPulse||0)+1);
    card.dataset.collisionPulse=id;
    card.style.setProperty('--collision-alpha',(0.96+Math.random()*0.04).toFixed(3));
    card.classList.remove('collision-pulse','collision-active');
    void card.offsetWidth;
    card.classList.add('collision-pulse','collision-active');
    window.setTimeout(()=>{
      if(card.dataset.collisionPulse===id){card.classList.remove('collision-pulse','collision-active');card.style.removeProperty('--collision-alpha')}
      /* 38ms true-dark gap before the next impact. */
      window.setTimeout(step,38);
    },82);
  };
  step();
}
function impactRing(kind,x,y){
  const ring=document.createElement('i');ring.className=`collision-hit-ring ${kind}`;ring.style.left=`${x}px`;ring.style.top=`${y}px`;layer.appendChild(ring);
  const anim=ring.animate([
    {transform:'translate(-50%,-50%) scale(.18)',opacity:1},
    {transform:'translate(-50%,-50%) scale(1.25)',opacity:.7,offset:.22},
    {transform:'translate(-50%,-50%) scale(3.2)',opacity:0}
  ],{duration:360,easing:'cubic-bezier(.16,1,.3,1)',fill:'forwards'});
  anim.finished.then(()=>ring.remove()).catch(()=>ring.remove());
}
function addEventParticle(kind,index,total){
  const a=source(),b=target(kind),dx=b.x-a.x,dy=b.y-a.y,dist=Math.hypot(dx,dy)||1,nx=-dy/dist,ny=dx/dist;
  const spread=(Math.random()-.5)*(kind==='accept'?82:88);
  const bend=(kind==='accept'?-58:58)+(Math.random()-.5)*28;
  const control={x:(a.x+b.x)*.5+nx*bend,y:(a.y+b.y)*.5+ny*bend};
  const el=document.createElement('i');el.className=`event-particle ${kind}`;
  const size=3.4+Math.random()*4.6;el.style.width=`${size}px`;el.style.height=`${size}px`;
  el.style.setProperty('--tail-size',`${12+Math.random()*15}px`);
  layer.appendChild(el);
  /* Readable but brisk flight, with impacts arriving in a tight visible chain. */
  const duration=(kind==='accept'?1820:1720)*(0.95+Math.random()*.10);
  const delay=index*92+Math.random()*18;
  const points=[0,.05,.11,.19,.29,.4,.52,.64,.74,.83,.9,.96,1].map(t=>{const p=bezier(a,control,b,t),s=Math.sin(Math.PI*t);return{x:p.x+nx*spread*s,y:p.y+ny*spread*s}});
  const frames=points.map((p,i)=>({transform:`translate3d(${p.x}px,${p.y}px,0) scale(${i===0?.2:i===1?.7:i>=points.length-2?1.45:1})`,opacity:i===0?0:i===1?.82:i>=points.length-2?1:.9}));
  const anim=el.animate(frames,{duration,delay,easing:'cubic-bezier(.17,.73,.16,1)',fill:'forwards'});
  anim.finished.then(()=>{impactRing(kind,b.x,b.y);pulseCounter(kind);el.remove()}).catch(()=>el.remove());
}
function spawnEventBurst(kind,count=12){for(let i=0;i<count;i++)addEventParticle(kind,i,count)}
function syncCounter(el,kind){
  let last=Number(el.textContent)||0;
  const obs=new MutationObserver(()=>{const n=Number(el.textContent)||0;if(n>last){const delta=Math.min(4,n-last);for(let s=0;s<delta;s++)spawnEventBurst(kind,12)}last=n});
  obs.observe(el,{childList:true,characterData:true,subtree:true});
}
syncCounter(accepted,'accept');
syncCounter(rejected,'reject');
})();
