(()=>{
'use strict';
if(window.__FIXEDCOIN_SHARE_IMPACT_V7__)return;
window.__FIXEDCOIN_SHARE_IMPACT_V7__=true;
const forge=document.getElementById('forge');
const stage=document.getElementById('forgeStage');
const accepted=document.getElementById('acceptedCount');
const rejected=document.getElementById('rejectedCount');
if(!forge||!stage||!accepted||!rejected)return;

const center=e=>{const r=e?.getBoundingClientRect();return r?{x:r.left+r.width/2,y:r.top+r.height/2}:null};
const card=k=>forge.querySelector(k==='accept'?'.accepted':'.rejected');
const source=()=>center(document.getElementById('forgeCore'))||center(forge);
const remove=e=>e?.remove();
const stageRect=()=>stage.getBoundingClientRect();
const local=p=>{const r=stageRect();return{x:p.x-r.left,y:p.y-r.top}};

function ensureLayer(){
  let layer=stage.querySelector('.share-event-layer');
  if(!layer){
    layer=document.createElement('div');
    layer.className='share-event-layer';
    layer.setAttribute('aria-hidden','true');
    stage.appendChild(layer);
  }
  return layer;
}

const baseTransform=k=>k==='accept'
  ?'perspective(800px) rotateY(calc(-12deg + var(--px,0deg))) rotateX(calc(2deg + var(--py,0deg))) translateZ(0)'
  :'perspective(800px) rotateY(calc(-12deg + var(--px,0deg))) rotateX(calc(1.5deg + var(--py,0deg))) translateZ(0)';

function smash(k){
  const el=card(k);if(!el)return;
  const base=baseTransform(k);
  el.animate([
    {transform:base,filter:'brightness(1)'},
    {transform:`${base} translate3d(4px,-2px,18px) scale(1.055)`,filter:'brightness(1.32)'},
    {transform:`${base} translate3d(-2px,2px,7px) scale(.992)`,filter:'brightness(1.12)'},
    {transform:`${base} translate3d(0,0,9px) scale(1.02)`,filter:'brightness(1.16)'},
    {transform:`${base} translate3d(0,0,0) scale(1)`,filter:'brightness(1)'}
  ],{duration:k==='accept'?1050:950,easing:'cubic-bezier(.16,.85,.25,1)',fill:'none'});
}

function flashDot(k){
  const el=card(k);if(!el)return;
  el.classList.remove('share-impact');void el.offsetWidth;el.classList.add('share-impact');
  window.setTimeout(()=>el.classList.remove('share-impact'),1050);
}

function bezier(a,c,b,t){const u=1-t;return{x:u*u*a.x+2*u*t*c.x+t*t*b.x,y:u*u*a.y+2*u*t*c.y+t*t*b.y};}

function particle(el,points,duration,delay=0){
  const frames=points.map((p,i)=>({
    transform:`translate3d(${p.x}px,${p.y}px,0) scale(${i===0?.2:i===points.length-1?1.45:1})`,
    opacity:i===0?0:i===1?.95:i===points.length-1?1:.72
  }));
  const a=el.animate(frames,{duration,delay,easing:'cubic-bezier(.18,.78,.2,1)',fill:'forwards'});
  a.finished.then(()=>remove(el)).catch(()=>remove(el));
}

function launchParticleStream(kind,start,end){
  const layer=ensureLayer();
  const a=local(start),b=local(end);
  const dx=b.x-a.x,dy=b.y-a.y,len=Math.hypot(dx,dy)||1;
  const nx=-dy/len,ny=dx/len;
  const bend=kind==='accept'?-82:82;
  const spread=kind==='accept'?82:98;
  const count=kind==='accept'?58:68;
  const duration=kind==='accept'?1900:1750;

  /* One authoritative direction: FIXCORE -> the share counter. Nothing is
     allowed to originate from the left metrics or travel away from the core. */
  const mid={x:(a.x+b.x)/2+nx*bend,y:(a.y+b.y)/2+ny*bend};
  const main=document.createElement('i');
  main.className=`share-flight ${kind}`;
  layer.appendChild(main);
  particle(main,[0,.12,.28,.46,.64,.8,.92,1].map(t=>bezier(a,mid,b,t)),duration);

  for(let i=0;i<count;i++){
    const p=document.createElement('i');
    p.className=`share-spark ${kind}`;
    const lateral=(Math.random()-.5)*spread;
    const tangent=(Math.random()-.5)*40;
    const control={x:mid.x+nx*lateral+dx/len*tangent,y:mid.y+ny*lateral+dy/len*tangent};
    const startOffset=(Math.random()-.5)*18;
    const endOffset=(Math.random()-.5)*Math.min(26,spread*.3);
    const startP={x:a.x+nx*startOffset,y:a.y+ny*startOffset};
    const endP={x:b.x+nx*endOffset,y:b.y+ny*endOffset};
    const t=[0,.08,.18,.32,.48,.64,.8,.92,1];
    const points=t.map(v=>bezier(startP,control,endP,v));
    const size=2.2+Math.random()*4.8;
    p.style.width=`${size}px`;p.style.height=`${size}px`;
    p.style.setProperty('--spark-alpha',String(.55+Math.random()*.45));
    layer.appendChild(p);
    particle(p,points,duration*(.78+Math.random()*.38),i*14+Math.random()*180);
  }

  /* Broad impact halo at the card, not a second stream. */
  const ring=document.createElement('i');
  ring.className=`share-impact-ring ${kind}`;
  ring.style.left=`${b.x}px`;ring.style.top=`${b.y}px`;
  layer.appendChild(ring);
  const ringAnim=ring.animate([
    {transform:'translate(-50%,-50%) scale(.35)',opacity:0},
    {transform:'translate(-50%,-50%) scale(1)',opacity:1,offset:.2},
    {transform:'translate(-50%,-50%) scale(2.8)',opacity:0}
  ],{duration:1150,delay:Math.max(0,duration-420),easing:'cubic-bezier(.16,1,.3,1)',fill:'forwards'});
  ringAnim.finished.then(()=>remove(ring)).catch(()=>remove(ring));
}

async function launch(k){
  const a=source(),target=card(k)?center(card(k)):null;
  if(!a||!target)return;
  launchParticleStream(k,a,target);
  await new Promise(resolve=>window.setTimeout(resolve,k==='accept'?1250:1120));
  flashDot(k);
  smash(k);
}

let la=+accepted.textContent||0,lr=+rejected.textContent||0,boot=true,active=0;
const observer=new MutationObserver(()=>{
  const a=+accepted.textContent||0,r=+rejected.textContent||0;
  if(!boot&&active<3){
    if(a>la){active++;launch('accept').finally(()=>active--)}
    if(r>lr){active++;launch('reject').finally(()=>active--)}
  }
  la=a;lr=r;boot=false;
});
observer.observe(accepted,{childList:true,characterData:true,subtree:true});
observer.observe(rejected,{childList:true,characterData:true,subtree:true});
})();
