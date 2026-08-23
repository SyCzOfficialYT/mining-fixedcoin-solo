(()=>{
'use strict';
if(window.__FIXEDCOIN_FORGE_COLLISION_V2__) return;
window.__FIXEDCOIN_FORGE_COLLISION_V2__=true;

const forge=document.getElementById('forge');
const stage=document.getElementById('forgeStage');
const core=document.getElementById('forgeCore');
const accepted=document.getElementById('acceptedCount');
const rejected=document.getElementById('rejectedCount');
if(!forge||!stage||!core||!accepted||!rejected)return;

const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
const center=el=>{const r=el.getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2}};
const local=p=>{const r=stage.getBoundingClientRect();return{x:p.x-r.left,y:p.y-r.top}};
const sourceCenter=()=>local(center(core));
const collisionRadius=()=>Math.min(stage.clientWidth,stage.clientHeight)*.20;

let layer=stage.querySelector('.collision-field');
if(!layer){layer=document.createElement('div');layer.className='collision-field';layer.setAttribute('aria-hidden','true');stage.appendChild(layer)}

let raf=0;
const particles=[];
const liveHits={accept:0,reject:0};
let seed=performance.now();

function pulseCounter(kind){
  const card=stage.querySelector(kind==='accept'?'.forge-counter.accepted':'.forge-counter.rejected');
  if(!card)return;
  const prev=Number(card.dataset.hitId||0)+1;card.dataset.hitId=String(prev);
  const strength=.55+Math.random()*.45;
  card.style.setProperty('--collision-alpha',strength.toFixed(3));
  card.classList.remove('collision-pulse');
  void card.offsetWidth;
  card.classList.add('collision-pulse');
  window.setTimeout(()=>{
    if(Number(card.dataset.hitId)===prev) card.classList.remove('collision-pulse');
  },260);
}

function spawn(kind,count){
  const c=sourceCenter();
  for(let i=0;i<count;i++){
    const a=Math.random()*Math.PI*2;
    const radius=collisionRadius()*(.62+Math.random()*.22);
    particles.push({
      kind,
      a,
      r:radius,
      speed:(kind==='accept'?-.0018:.0018)*(0.82+Math.random()*.42),
      radial:(Math.random()<.5?-1:1)*(.018+Math.random()*.028),
      wobble:Math.random()*6.28,
      phase:Math.random()*6.28,
      life:0,
      ttl:1200+Math.random()*1100,
      size:1.6+Math.random()*2.8,
      alpha:.45+Math.random()*.45,
      hit:false,
      x:c.x,y:c.y
    });
  }
  while(particles.length>420)particles.shift();
}

function updateParticle(p,dt,now){
  const c=sourceCenter();
  p.life+=dt;
  p.a+=p.speed*dt;
  p.r+=p.radial*dt;
  const wob=Math.sin(now*.003+p.phase)*6;
  p.r=clamp(p.r,collisionRadius()*.12,collisionRadius()*1.06);
  p.x=c.x+Math.cos(p.a)*(p.r+wob);
  p.y=c.y+Math.sin(p.a)*(p.r+wob)*.82;

  const hitR=collisionRadius();
  const dist=Math.hypot(p.x-c.x,p.y-c.y);
  if(!p.hit && dist<=hitR+2){
    p.hit=true;
    liveHits[p.kind]++;
    pulseCounter(p.kind);
    spawnCollisionRing(p.kind,p.x,p.y);
  }
  return p.life<p.ttl;
}

function spawnCollisionRing(kind,x,y){
  const ring=document.createElement('i');
  ring.className=`collision-hit-ring ${kind}`;
  ring.style.left=`${x}px`;ring.style.top=`${y}px`;
  layer.appendChild(ring);
  const a=ring.animate([
    {transform:'translate(-50%,-50%) scale(.35)',opacity:.95},
    {transform:'translate(-50%,-50%) scale(1.6)',opacity:.45,offset:.45},
    {transform:'translate(-50%,-50%) scale(2.8)',opacity:0}
  ],{duration:360,easing:'cubic-bezier(.16,1,.3,1)',fill:'forwards'});
  a.finished.then(()=>ring.remove()).catch(()=>ring.remove());
}

function draw(now){
  const dead=[];
  for(const p of particles){
    if(!updateParticle(p,16,now)) dead.push(p);
  }
  for(const p of dead){const i=particles.indexOf(p);if(i>=0)particles.splice(i,1)}
  // Render DOM particles only; they stay fully inside the center field.
  const alive=new Set();
  for(const p of particles){
    if(!p.el){
      p.el=document.createElement('i');
      p.el.className=`collision-particle ${p.kind}`;
      layer.appendChild(p.el);
    }
    alive.add(p.el);
    const fade=Math.min(1,p.life/180)*Math.min(1,(p.ttl-p.life)/260);
    p.el.style.width=`${p.size}px`;
    p.el.style.height=`${p.size}px`;
    p.el.style.opacity=String(Math.max(0,fade*p.alpha));
    p.el.style.transform=`translate3d(${p.x}px,${p.y}px,0)`;
  }
  layer.querySelectorAll('.collision-particle').forEach(el=>{if(!alive.has(el))el.remove()});
  raf=requestAnimationFrame(draw);
}

function syncCounter(el,kind){
  let last=Number(el.textContent)||0;
  const obs=new MutationObserver(()=>{
    const n=Number(el.textContent)||0;
    if(n>last){const delta=Math.min(12,n-last);spawn(kind,Math.max(8,delta*7));}
    last=n;
  });
  obs.observe(el,{childList:true,characterData:true,subtree:true});
}

// Warm start with a restrained center field; shares add the meaningful bursts.
spawn('accept',12);spawn('reject',4);
syncCounter(accepted,'accept');
syncCounter(rejected,'reject');
requestAnimationFrame(draw);

window.addEventListener('beforeunload',()=>cancelAnimationFrame(raf),{once:true});
})();
