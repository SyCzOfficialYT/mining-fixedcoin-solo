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

const center=el=>{const r=el.getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2}};
const local=p=>{const r=stage.getBoundingClientRect();return{x:p.x-r.left,y:p.y-r.top}};
const sourceCenter=()=>local(center(core));
const collisionRadius=()=>Math.min(stage.clientWidth,stage.clientHeight)*.20;

let layer=stage.querySelector('.collision-field');
if(!layer){layer=document.createElement('div');layer.className='collision-field';layer.setAttribute('aria-hidden','true');stage.appendChild(layer)}

let raf=0;
const particles=[];

function pulseCounter(kind){
  const card=stage.querySelector(kind==='accept'?'.forge-counter.accepted':'.forge-counter.rejected');
  if(!card)return;
  const strength=.72+Math.random()*.28;
  card.style.setProperty('--collision-alpha',strength.toFixed(3));
  card.classList.remove('collision-pulse');
  void card.offsetWidth;
  card.classList.add('collision-pulse');
  window.setTimeout(()=>card.classList.remove('collision-pulse'),220);
}

function spawn(kind,count){
  const c=sourceCenter(),R=collisionRadius();
  for(let i=0;i<count;i++){
    const a=Math.random()*Math.PI*2;
    const radius=R*(.18+Math.random()*.18);
    particles.push({
      kind,
      a,
      r:radius,
      speed:(kind==='accept'?-1:1)*(.0007+Math.random()*.00055),
      radial:.020+Math.random()*.024,
      phase:Math.random()*6.28,
      life:0,
      ttl:1500+Math.random()*1200,
      size:1.8+Math.random()*2.8,
      alpha:.55+Math.random()*.42,
      prevDist:radius,
      hit:false,
      x:c.x,y:c.y
    });
  }
  while(particles.length>520)particles.shift();
}

function updateParticle(p,dt,now){
  const c=sourceCenter(),R=collisionRadius();
  p.life+=dt;
  p.a+=p.speed*dt;
  p.r=Math.min(R*1.08,p.r+p.radial*dt);

  const wob=Math.sin(now*.003+p.phase)*5;
  p.x=c.x+Math.cos(p.a)*(p.r+wob);
  p.y=c.y+Math.sin(p.a)*(p.r+wob)*.82;
  const dist=Math.hypot(p.x-c.x,p.y-c.y);

  // Spawned particles start inside the ring and travel outward. Exactly one
  // crossing => exactly one counter pulse for that individual particle.
  if(!p.hit && p.prevDist<R && dist>=R){
    p.hit=true;
    pulseCounter(p.kind);
    spawnCollisionRing(p.kind,p.x,p.y);
  }
  p.prevDist=dist;
  return p.life<p.ttl && p.r<R*1.08;
}

function spawnCollisionRing(kind,x,y){
  const ring=document.createElement('i');
  ring.className=`collision-hit-ring ${kind}`;
  ring.style.left=`${x}px`;ring.style.top=`${y}px`;
  layer.appendChild(ring);
  const a=ring.animate([
    {transform:'translate(-50%,-50%) scale(.25)',opacity:.98},
    {transform:'translate(-50%,-50%) scale(1.45)',opacity:.55,offset:.38},
    {transform:'translate(-50%,-50%) scale(3)',opacity:0}
  ],{duration:340,easing:'cubic-bezier(.16,1,.3,1)',fill:'forwards'});
  a.finished.then(()=>ring.remove()).catch(()=>ring.remove());
}

function draw(now){
  const current=performance.now();
  const dt=Math.min(34,Math.max(8,current-(draw.last||current)));draw.last=current;
  const dead=[];
  for(const p of particles){if(!updateParticle(p,dt,now))dead.push(p)}
  for(const p of dead){const i=particles.indexOf(p);if(i>=0)particles.splice(i,1)}

  const alive=new Set();
  for(const p of particles){
    if(!p.el){p.el=document.createElement('i');p.el.className=`collision-particle ${p.kind}`;layer.appendChild(p.el)}
    alive.add(p.el);
    const fade=Math.min(1,p.life/140)*Math.min(1,(p.ttl-p.life)/260);
    p.el.style.width=`${p.size}px`;p.el.style.height=`${p.size}px`;
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
    if(n>last){
      const delta=Math.min(12,n-last);
      spawn(kind,Math.max(10,delta*9));
    }
    last=n;
  });
  obs.observe(el,{childList:true,characterData:true,subtree:true});
}

spawn('accept',8);spawn('reject',4);
syncCounter(accepted,'accept');
syncCounter(rejected,'reject');
requestAnimationFrame(draw);
window.addEventListener('beforeunload',()=>cancelAnimationFrame(raf),{once:true});
})();
