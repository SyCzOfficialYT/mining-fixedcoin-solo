(()=>{
'use strict';
if(window.__FIXEDCOIN_FORGE_COLLISION_V8__) return;
window.__FIXEDCOIN_FORGE_COLLISION_V8__=true;
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

/* Every particle has its own impact pulse. There is NO shared state/queue:
   arrival #1 flashes the card, then goes dark; arrival #2 flashes it again,
   and so on. This makes the physical particle contact the source of truth. */
function pulseCounter(kind){
  const card=stage.querySelector(kind==='accept'?'.forge-counter.accepted':'.forge-counter.rejected');
  if(!card)return;

  const color=kind==='accept'?'77,255,112':'255,78,78';
  const hot=kind==='accept'?'#baffc7':'#ffd0cc';
  const darkShadow=kind==='accept'
    ?'0 14px 30px rgba(0,0,0,.42), inset 0 0 0 1px rgba(255,255,255,.018)'
    :'0 14px 30px rgba(0,0,0,.42), inset 0 0 0 1px rgba(255,255,255,.018)';
  const brightShadow=`0 0 8px rgba(${color},.92),0 0 18px rgba(${color},.72),0 0 38px rgba(${color},.45),0 0 64px rgba(${color},.22),0 14px 30px rgba(0,0,0,.42),inset 0 0 22px rgba(${color},.12)`;

  /* Web Animations gives every hit its own animation instance. It therefore
     cannot get stuck in the old "one long glowing state" behaviour. */
  const anim=card.animate([
    {boxShadow:darkShadow,filter:'brightness(1)',borderColor:`rgba(${color},.16)`,offset:0},
    {boxShadow:brightShadow,filter:'brightness(1.42)',borderColor:`rgba(${color},.98)`,offset:.18},
    {boxShadow:brightShadow,filter:'brightness(1.26)',borderColor:`rgba(${color},.92)`,offset:.46},
    {boxShadow:darkShadow,filter:'brightness(1)',borderColor:`rgba(${color},.16)`,offset:.64},
    {boxShadow:darkShadow,filter:'brightness(1)',borderColor:`rgba(${color},.16)`,offset:1}
  ],{duration:92,easing:'steps(1,end)',fill:'none'});

  const strong=card.querySelector('strong');
  const icon=card.querySelector('i');
  const strongAnim=strong?.animate([
    {color:'rgba(104,255,134,.82)',textShadow:'none',offset:0},
    {color:hot,textShadow:`0 0 12px rgba(${color},.8),0 0 24px rgba(${color},.35)`,offset:.18},
    {color:hot,textShadow:`0 0 8px rgba(${color},.62)`,offset:.5},
    {color:'rgba(104,255,134,.82)',textShadow:'none',offset:.66},
    {color:'rgba(104,255,134,.82)',textShadow:'none',offset:1}
  ],{duration:92,easing:'steps(1,end)',fill:'none'});
  const iconAnim=icon?.animate([
    {color:'rgba(104,255,134,.58)',borderColor:`rgba(${color},.28)`,boxShadow:'none',offset:0},
    {color:hot,borderColor:`rgba(${color},1)`,boxShadow:`0 0 10px rgba(${color},.98),0 0 24px rgba(${color},.62)`,offset:.18},
    {color:hot,borderColor:`rgba(${color},.9)`,boxShadow:`0 0 7px rgba(${color},.75),0 0 16px rgba(${color},.38)`,offset:.5},
    {color:'rgba(104,255,134,.58)',borderColor:`rgba(${color},.28)`,boxShadow:'none',offset:.66},
    {color:'rgba(104,255,134,.58)',borderColor:`rgba(${color},.28)`,boxShadow:'none',offset:1}
  ],{duration:92,easing:'steps(1,end)',fill:'none'});
  anim.finished.catch(()=>{});strongAnim?.finished.catch(()=>{});iconAnim?.finished.catch(()=>{});
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
  const size=3.6+Math.random()*4.8;el.style.width=`${size}px`;el.style.height=`${size}px`;
  el.style.setProperty('--tail-size',`${14+Math.random()*18}px`);
  layer.appendChild(el);
  const duration=(kind==='accept'?1900:1800)*(0.95+Math.random()*.10);
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
