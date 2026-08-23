(()=>{
'use strict';
if(window.__FIXEDCOIN_FORGE_COLLISION_V3__) return;
window.__FIXEDCOIN_FORGE_COLLISION_V3__=true;

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

function pulseCounter(kind){
  const card=stage.querySelector(kind==='accept'?'.forge-counter.accepted':'.forge-counter.rejected');
  if(!card)return;
  const strength=.84+Math.random()*.16;
  const id=String(Number(card.dataset.collisionPulse||0)+1);
  card.dataset.collisionPulse=id;
  card.style.setProperty('--collision-alpha',strength.toFixed(3));
  card.classList.remove('collision-pulse','collision-active');
  void card.offsetWidth;
  card.classList.add('collision-pulse','collision-active');
  window.setTimeout(()=>{if(card.dataset.collisionPulse===id){card.classList.remove('collision-pulse','collision-active');card.style.removeProperty('--collision-alpha')}},300);
}

function impactRing(kind,x,y){
  const ring=document.createElement('i');ring.className=`collision-hit-ring ${kind}`;ring.style.left=`${x}px`;ring.style.top=`${y}px`;layer.appendChild(ring);
  const anim=ring.animate([
    {transform:'translate(-50%,-50%) scale(.25)',opacity:.98},
    {transform:'translate(-50%,-50%) scale(1.35)',opacity:.65,offset:.34},
    {transform:'translate(-50%,-50%) scale(3)',opacity:0}
  ],{duration:380,easing:'cubic-bezier(.16,1,.3,1)',fill:'forwards'});
  anim.finished.then(()=>ring.remove()).catch(()=>ring.remove());
}

function addEventParticle(kind,index,count){
  const a=source(),b=target(kind),dx=b.x-a.x,dy=b.y-a.y,dist=Math.hypot(dx,dy)||1,nx=-dy/dist,ny=dx/dist;
  const spread=(Math.random()-.5)*(kind==='accept'?42:48);
  const bend=(kind==='accept'?-42:42)+ (Math.random()-.5)*24;
  const control={x:(a.x+b.x)*.5+nx*bend,y:(a.y+b.y)*.5+ny*bend};
  const el=document.createElement('i');el.className=`event-particle ${kind}`;const size=2.3+Math.random()*3.1;el.style.width=`${size}px`;el.style.height=`${size}px`;layer.appendChild(el);
  const duration=(kind==='accept'?1080:1020)*(0.82+Math.random()*.25),delay=index*9+Math.random()*110;
  const points=[0,.08,.2,.34,.5,.66,.8,.91,.97,1].map(t=>{const p=bezier(a,control,b,t);const s=Math.sin(Math.PI*t);return{x:p.x+nx*spread*s,y:p.y+ny*spread*s}});
  const frames=points.map((p,i)=>({transform:`translate3d(${p.x}px,${p.y}px,0) scale(${i===0?.28:i>points.length-3?1.45:1})`,opacity:i===0?.05:i<2?.92:i===points.length-1?1:.8}));
  const anim=el.animate(frames,{duration,delay,easing:'cubic-bezier(.18,.78,.18,1)',fill:'forwards'});
  anim.finished.then(()=>{impactRing(kind,b.x,b.y);pulseCounter(kind);el.remove()}).catch(()=>el.remove());
}

function spawnEventBurst(kind,count){for(let i=0;i<count;i++)addEventParticle(kind,i,count)}

function syncCounter(el,kind){
  let last=Number(el.textContent)||0;
  const obs=new MutationObserver(()=>{
    const n=Number(el.textContent)||0;
    if(n>last){const delta=Math.min(4,n-last);for(let s=0;s<delta;s++)spawnEventBurst(kind,16)}
    last=n;
  });
  obs.observe(el,{childList:true,characterData:true,subtree:true});
}

syncCounter(accepted,'accept');
syncCounter(rejected,'reject');
})();
