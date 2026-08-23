(()=>{
'use strict';
if(window.__FIXEDCOIN_FORGE_COLLISION_V4__) return;
window.__FIXEDCOIN_FORGE_COLLISION_V4__=true;

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

/* Each collision is deliberately isolated. The next particle does not arrive
   until the previous neon pulse has completed, so the visual state is strictly:
   OFF -> ON -> OFF -> ON -> OFF ... one particle at a time. */
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
    card.style.setProperty('--collision-alpha',(0.9+Math.random()*0.1).toFixed(3));
    card.classList.remove('collision-pulse','collision-active');
    void card.offsetWidth;
    card.classList.add('collision-pulse','collision-active');
    window.setTimeout(()=>{
      if(card.dataset.collisionPulse===id){
        card.classList.remove('collision-pulse','collision-active');
        card.style.removeProperty('--collision-alpha');
      }
      /* Explicit dark interval before the next particle lights the card. */
      window.setTimeout(step,120);
    },240);
  };
  step();
}

function impactRing(kind,x,y){
  const ring=document.createElement('i');ring.className=`collision-hit-ring ${kind}`;ring.style.left=`${x}px`;ring.style.top=`${y}px`;layer.appendChild(ring);
  const anim=ring.animate([
    {transform:'translate(-50%,-50%) scale(.25)',opacity:.98},
    {transform:'translate(-50%,-50%) scale(1.3)',opacity:.6,offset:.34},
    {transform:'translate(-50%,-50%) scale(3)',opacity:0}
  ],{duration:420,easing:'cubic-bezier(.16,1,.3,1)',fill:'forwards'});
  anim.finished.then(()=>ring.remove()).catch(()=>ring.remove());
}

function addEventParticle(kind,index,count){
  const a=source(),b=target(kind),dx=b.x-a.x,dy=b.y-a.y,dist=Math.hypot(dx,dy)||1,nx=-dy/dist,ny=dx/dist;
  const spread=(Math.random()-.5)*(kind==='accept'?42:48);
  const bend=(kind==='accept'?-42:42)+(Math.random()-.5)*24;
  const control={x:(a.x+b.x)*.5+nx*bend,y:(a.y+b.y)*.5+ny*bend};
  const el=document.createElement('i');
  el.className=`event-particle ${kind}`;
  const size=2.4+Math.random()*3.2;
  el.style.width=`${size}px`;el.style.height=`${size}px`;
  layer.appendChild(el);

  /* Slow, readable flight. Ten particles are intentionally spread across the
     route so every impact can be seen and can produce its own OFF/ON pulse. */
  const duration=(kind==='accept'?2200:2050)*(0.92+Math.random()*.12);
  const delay=index*360+Math.random()*50;
  const points=[0,.07,.16,.28,.42,.56,.68,.78,.88,.95,1].map(t=>{
    const p=bezier(a,control,b,t),s=Math.sin(Math.PI*t);
    return{x:p.x+nx*spread*s,y:p.y+ny*spread*s};
  });
  const frames=points.map((p,i)=>({
    transform:`translate3d(${p.x}px,${p.y}px,0) scale(${i===0?.3:i>points.length-3?1.5:1})`,
    opacity:i===0?.03:i<2?.95:i===points.length-1?1:.82
  }));
  const anim=el.animate(frames,{duration,delay,easing:'cubic-bezier(.18,.78,.18,1)',fill:'forwards'});
  anim.finished.then(()=>{
    impactRing(kind,b.x,b.y);
    pulseCounter(kind);
    el.remove();
  }).catch(()=>el.remove());
}

function spawnEventBurst(kind,count=10){
  const n=Math.max(1,Math.min(10,count));
  for(let i=0;i<n;i++)addEventParticle(kind,i,n);
}

function syncCounter(el,kind){
  let last=Number(el.textContent)||0;
  const obs=new MutationObserver(()=>{
    const n=Number(el.textContent)||0;
    if(n>last){
      const delta=Math.min(4,n-last);
      for(let s=0;s<delta;s++)spawnEventBurst(kind,10);
    }
    last=n;
  });
  obs.observe(el,{childList:true,characterData:true,subtree:true});
}

syncCounter(accepted,'accept');
syncCounter(rejected,'reject');
})();
