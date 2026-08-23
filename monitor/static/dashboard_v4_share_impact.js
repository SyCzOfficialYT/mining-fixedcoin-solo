(()=>{
'use strict';
if(window.__FIXEDCOIN_SHARE_IMPACT_V8__)return;
window.__FIXEDCOIN_SHARE_IMPACT_V8__=true;

const forge=document.getElementById('forge');
const stage=document.getElementById('forgeStage');
const accepted=document.getElementById('acceptedCount');
const rejected=document.getElementById('rejectedCount');
const acceptedCard=document.getElementById('acceptedCounter');
const rejectedCard=document.getElementById('rejectedCounter');
const core=document.getElementById('forgeCore');
if(!forge||!stage||!accepted||!rejected||!core)return;

const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
const center=e=>{const r=e?.getBoundingClientRect();return r?{x:r.left+r.width/2,y:r.top+r.height/2}:null};
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

function collisionBurst(kind){
  const layer=ensureLayer();
  const cp=local(center(core));
  const card=kind==='accept'?acceptedCard:rejectedCard;
  if(!cp||!card)return;

  const maxCount=kind==='accept'?34:38;
  const threshold=kind==='accept'?8:10;
  const ringRadius=Math.min(stage.clientWidth,stage.clientHeight)*.19;
  const spread=kind==='accept'?0.95:1.05;
  const angleCenter=kind==='accept'?-0.18:0.56;
  let collisions=0;
  let settled=false;
  const started=performance.now();

  card.classList.remove('collision-active');
  card.style.setProperty('--collision-alpha','0');
  card.style.setProperty('--collision-count','0');

  const finish=()=>{
    if(settled)return;
    settled=true;
    window.setTimeout(()=>{
      card.classList.remove('collision-active');
      card.style.removeProperty('--collision-alpha');
      card.style.removeProperty('--collision-count');
    },650);
  };

  const registerCollision=()=>{
    collisions++;
    const ratio=clamp(collisions/threshold,0,1);
    card.style.setProperty('--collision-alpha',String(.18+.82*ratio));
    card.style.setProperty('--collision-count',String(collisions));
    if(collisions>=1)card.classList.add('collision-active');

    if(collisions===threshold){
      smash(card,kind,ratio);
      flashDot(card,kind);
      forge.classList.remove('hit-accept','hit-reject');
      void forge.offsetWidth;
      forge.classList.add(kind==='accept'?'hit-accept':'hit-reject');
      window.setTimeout(()=>forge.classList.remove(kind==='accept'?'hit-accept':'hit-reject'),850);
    }
  };

  for(let i=0;i<maxCount;i++){
    const p=document.createElement('i');
    p.className=`collision-particle ${kind}`;
    const angle=angleCenter+(Math.random()-.5)*spread;
    const startR=16+Math.random()*18;
    const endR=ringRadius*(.72+Math.random()*.38);
    const sx=cp.x+Math.cos(angle)*startR;
    const sy=cp.y+Math.sin(angle)*startR;
    const ex=cp.x+Math.cos(angle)*endR;
    const ey=cp.y+Math.sin(angle)*endR*.72;
    const bend=(Math.random()-.5)*28;
    const cx=(sx+ex)/2-Math.sin(angle)*bend;
    const cy=(sy+ey)/2+Math.cos(angle)*bend;
    p.style.width=`${1.5+Math.random()*3}px`;
    p.style.height=p.style.width;
    layer.appendChild(p);

    const duration=520+Math.random()*520;
    const delay=Math.random()*260;
    const frames=[
      {transform:`translate3d(${sx}px,${sy}px,0) scale(.25)`,opacity:0},
      {transform:`translate3d(${cx}px,${cy}px,0) scale(1)`,opacity:.9,offset:.48},
      {transform:`translate3d(${ex}px,${ey}px,0) scale(1.35)`,opacity:1,offset:.88},
      {transform:`translate3d(${ex}px,${ey}px,0) scale(.05)`,opacity:0}
    ];
    const anim=p.animate(frames,{duration,delay,easing:'cubic-bezier(.18,.78,.2,1)',fill:'forwards'});
    anim.finished.then(()=>{
      registerCollision();
      p.remove();
    }).catch(()=>p.remove());
  }

  // A subtle collision halo remains around the core, never travels to the cards.
  const ring=document.createElement('i');
  ring.className=`collision-ring ${kind}`;
  ring.style.left=`${cp.x}px`;
  ring.style.top=`${cp.y}px`;
  layer.appendChild(ring);
  const ringAnim=ring.animate([
    {transform:'translate(-50%,-50%) scale(.3)',opacity:0},
    {transform:'translate(-50%,-50%) scale(1)',opacity:.9,offset:.22},
    {transform:'translate(-50%,-50%) scale(7)',opacity:0}
  ],{duration:900,easing:'cubic-bezier(.16,1,.3,1)',fill:'forwards'});
  ringAnim.finished.then(()=>ring.remove()).catch(()=>ring.remove());

  window.setTimeout(()=>{if(!settled){registerCollision();finish()}},1800);
  window.setTimeout(finish,2400);
}

function smash(el,kind,intensity){
  const base=kind==='accept'
    ?'perspective(800px) rotateY(-12deg) rotateX(2deg) translateZ(0)'
    :'perspective(800px) rotateY(-12deg) rotateX(1.5deg) translateZ(0)';
  const scale=1+.025*intensity;
  el.animate([
    {transform:base,filter:'brightness(1)'},
    {transform:`${base} translate3d(3px,-1px,12px) scale(${scale})`,filter:'brightness(1.22)'},
    {transform:`${base} translate3d(-2px,2px,5px) scale(.995)`,filter:'brightness(1.08)'},
    {transform:`${base} translate3d(0,0,4px) scale(1.01)`,filter:'brightness(1.12)'},
    {transform:`${base} translate3d(0,0,0) scale(1)`,filter:'brightness(1)'}
  ],{duration:kind==='accept'?720:680,easing:'cubic-bezier(.16,.85,.25,1)',fill:'none'});
}

function flashDot(card,kind){
  const dot=card.querySelector('.event-dot');
  if(!dot)return;
  dot.classList.remove('event-collision-flash');
  void dot.offsetWidth;
  dot.classList.add('event-collision-flash');
  dot.style.opacity='1';
  dot.style.visibility='visible';
  window.setTimeout(()=>{
    dot.style.opacity='0';
    dot.style.visibility='hidden';
    dot.classList.remove('event-collision-flash');
  },720);
}

let la=+accepted.textContent||0;
let lr=+rejected.textContent||0;
let boot=true;
let active=0;
const observer=new MutationObserver(()=>{
  const a=+accepted.textContent||0;
  const r=+rejected.textContent||0;
  if(!boot&&active<3){
    if(a>la){active++;collisionBurst('accept');window.setTimeout(()=>active--,1200)}
    if(r>lr){active++;collisionBurst('reject');window.setTimeout(()=>active--,1200)}
  }
  la=a;lr=r;boot=false;
});
observer.observe(accepted,{childList:true,characterData:true,subtree:true});
observer.observe(rejected,{childList:true,characterData:true,subtree:true});
})();
