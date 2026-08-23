(()=>{
'use strict';
if(window.__FIXEDCOIN_SHARE_IMPACT_V6__)return;
window.__FIXEDCOIN_SHARE_IMPACT_V6__=true;
const forge=document.getElementById('forge');
const stage=document.getElementById('forgeStage');
const accepted=document.getElementById('acceptedCount');
const rejected=document.getElementById('rejectedCount');
if(!forge||!stage||!accepted||!rejected)return;

const center=e=>{
  const r=e?.getBoundingClientRect();
  return r?{x:r.left+r.width/2,y:r.top+r.height/2}:null;
};
const card=k=>forge.querySelector(k==='accept'?'.accepted':'.rejected');
const dotEl=k=>forge.querySelector(k==='accept'?'.accepted .event-dot':'.rejected .event-dot');
const dot=k=>center(dotEl(k));
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
  const el=card(k);
  if(!el)return;
  const base=baseTransform(k);
  el.animate([
    {transform:base,filter:'brightness(1)'},
    {transform:`${base} translate3d(4px,-2px,14px) scale(1.045)`,filter:'brightness(1.25)'},
    {transform:`${base} translate3d(-3px,2px,5px) scale(.988)`,filter:'brightness(1.08)'},
    {transform:`${base} translate3d(1px,0,7px) scale(1.014)`,filter:'brightness(1.12)'},
    {transform:`${base} translate3d(0,0,0) scale(1)`,filter:'brightness(1)'}
  ],{duration:k==='accept'?900:820,easing:'cubic-bezier(.16,.85,.25,1)',fill:'none'});
}

function flashDot(k){
  const d=dotEl(k);
  if(!d)return;
  d.style.setProperty('display','block','important');
  d.style.setProperty('visibility','visible','important');
  d.style.setProperty('opacity','1','important');
  d.style.setProperty('transform','scale(1.35)','important');
  window.setTimeout(()=>{
    d.style.setProperty('display','none','important');
    d.style.setProperty('visibility','hidden','important');
    d.style.setProperty('opacity','0','important');
    d.style.setProperty('transform','scale(.45)','important');
  },1050);
}

function bezier(a,c,b,t){
  const u=1-t;
  return {x:u*u*a.x+2*u*t*c.x+t*t*b.x,y:u*u*a.y+2*u*t*c.y+t*t*b.y};
}

function animateParticle(el,points,duration,delay=0){
  const frames=points.map((p,i)=>({
    transform:`translate3d(${p.x}px,${p.y}px,0) scale(${i===0?.45:i===points.length-1?1.15:1})`,
    opacity:i===0?0:i===1?.95:i===points.length-1?1:.8
  }));
  const anim=el.animate(frames,{duration,delay,easing:'linear',fill:'forwards'});
  anim.finished.then(()=>remove(el)).catch(()=>remove(el));
}

function launchParticleStream(kind,start,end){
  const layer=ensureLayer();
  const a=local(start),b=local(end);
  const dx=b.x-a.x,dy=b.y-a.y;
  const len=Math.hypot(dx,dy)||1;
  const nx=-dy/len,ny=dx/len;
  const direction=kind==='accept'?-1:1;
  const mid={x:(a.x+b.x)/2,y:(a.y+b.y)/2+direction*46};
  const count=kind==='accept'?34:40;

  const main=document.createElement('i');
  main.className=`share-flight ${kind}`;
  layer.appendChild(main);
  const mainPoints=[0,.16,.34,.52,.7,.86,1].map(t=>bezier(a,mid,b,t));
  animateParticle(main,mainPoints,kind==='accept'?1450:1320,0);

  for(let i=0;i<count;i++){
    const p=document.createElement('i');
    p.className=`share-spark ${kind}`;
    const spread=(Math.random()-.5)*(kind==='accept'?52:64);
    const control={x:mid.x+nx*spread,y:mid.y+ny*spread};
    const offset=(Math.random()-.5)*34;
    const startP={x:a.x+nx*offset*.25,y:a.y+ny*offset*.25};
    const endP={x:b.x+nx*offset,y:b.y+ny*offset};
    const framesT=[0,.12,.28,.46,.64,.8,1];
    const points=framesT.map(t=>bezier(startP,control,endP,t));
    p.style.width=`${2+Math.random()*4}px`;
    p.style.height=`${2+Math.random()*4}px`;
    layer.appendChild(p);
    animateParticle(p,points,1150+Math.random()*650,i*24+Math.random()*90);
  }
}

function pulseAtTarget(kind,p){
  const layer=ensureLayer();
  const localP=local(p);
  const ring=document.createElement('i');
  ring.className=`share-spark ${kind}`;
  ring.style.width='14px';
  ring.style.height='14px';
  ring.style.margin='-7px 0 0 -7px';
  layer.appendChild(ring);
  const ringAnim=ring.animate([
    {transform:`translate3d(${localP.x}px,${localP.y}px,0) scale(.4)`,opacity:.95},
    {transform:`translate3d(${localP.x}px,${localP.y}px,0) scale(4.8)`,opacity:0}
  ],{duration:900,easing:'cubic-bezier(.16,1,.3,1)',fill:'forwards'});
  ringAnim.finished.then(()=>remove(ring)).catch(()=>remove(ring));
}

async function launch(k){
  const a=source(),b=dot(k);
  if(!a||!b)return;
  launchParticleStream(k,a,b);
  await new Promise(resolve=>window.setTimeout(resolve,k==='accept'?520:470));
  flashDot(k);
  smash(k);
  pulseAtTarget(k,b);
}

let la=+accepted.textContent||0;
let lr=+rejected.textContent||0;
let boot=true;
let active=0;
const observer=new MutationObserver(()=>{
  const a=+accepted.textContent||0;
  const r=+rejected.textContent||0;
  if(!boot&&active<3){
    if(a>la){active++;launch('accept').finally(()=>active--)}
    if(r>lr){active++;launch('reject').finally(()=>active--)}
  }
  la=a;
  lr=r;
  boot=false;
});
observer.observe(accepted,{childList:true,characterData:true,subtree:true});
observer.observe(rejected,{childList:true,characterData:true,subtree:true});
})();
