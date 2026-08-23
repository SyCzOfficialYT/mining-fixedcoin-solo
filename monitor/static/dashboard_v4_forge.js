(()=>{
'use strict';
if(window.__FIXEDCOIN_FORGE_V2__)return;
window.__FIXEDCOIN_FORGE_V2__=true;
const forge=document.getElementById('forge');
const core=document.getElementById('forgeCore');
if(!forge||!core)return;
let lastAccept=Number(document.getElementById('acceptedCount')?.textContent)||0;
let lastReject=Number(document.getElementById('rejectedCount')?.textContent)||0;
let booted=false;
const pulse=(kind,ms=820)=>{
  forge.classList.remove('hit-accept','hit-reject','hit-block','hit-round');
  void forge.offsetWidth;
  forge.classList.add(kind);
  window.setTimeout(()=>forge.classList.remove(kind),ms);
};
function spawnDust(kind){
  const stage=document.getElementById('forgeStage');
  if(!stage)return;
  const source=core.getBoundingClientRect();
  const target=stage.getBoundingClientRect();
  const ox=source.left+source.width/2-target.left;
  const oy=source.top+source.height/2-target.top;
  const count=kind==='accept'?18:22;
  for(let i=0;i<count;i++){
    const dust=document.createElement('i');
    dust.className=`forge-dust ${kind}`;
    dust.style.left=`${ox}px`;
    dust.style.top=`${oy}px`;
    stage.appendChild(dust);
    const angle=Math.random()*Math.PI*2;
    const distance=35+Math.random()*105;
    const dx=Math.cos(angle)*distance;
    const dy=Math.sin(angle)*distance;
    const scale=.65+Math.random()*.9;
    const duration=900+Math.random()*650;
    dust.animate([
      {transform:'translate3d(-50%,-50%,0) scale(.25)',opacity:0},
      {transform:`translate3d(calc(-50% + ${dx*.18}px),calc(-50% + ${dy*.18}px),0) scale(${scale})`,opacity:.9},
      {transform:`translate3d(calc(-50% + ${dx}px),calc(-50% + ${dy}px),0) scale(.15)`,opacity:0}
    ],{duration,easing:'cubic-bezier(.16,.8,.25,1)',fill:'forwards'}).finished.then(()=>dust.remove()).catch(()=>dust.remove());
  }
}
function accept(){spawnDust('accept');pulse('hit-accept',900)}
function reject(){spawnDust('reject');pulse('hit-reject',820)}
function block(){pulse('hit-block',1600)}
function round(){pulse('hit-round',1100)}
window.addEventListener('fixedcoin:accept',accept);
window.addEventListener('fixedcoin:reject',reject);
window.addEventListener('fixedcoin:block',block);
window.addEventListener('fixedcoin:round',round);
const observer=new MutationObserver(()=>{
  const a=Number(document.getElementById('acceptedCount')?.textContent)||0;
  const r=Number(document.getElementById('rejectedCount')?.textContent)||0;
  if(booted){
    if(a>lastAccept)accept();
    if(r>lastReject)reject();
  }
  lastAccept=a;
  lastReject=r;
  booted=true;
});
const accepted=document.getElementById('acceptedCount');
const rejected=document.getElementById('rejectedCount');
if(accepted)observer.observe(accepted,{childList:true,characterData:true,subtree:true});
if(rejected)observer.observe(rejected,{childList:true,characterData:true,subtree:true});
})();
