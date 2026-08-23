(()=>{
'use strict';
const stage=document.querySelector('.forge-stage');
if(!stage||stage.dataset.cardParallax==='1')return;
stage.dataset.cardParallax='1';
const cards=[...stage.querySelectorAll('.mine-metric,.forge-counter')];
if(!cards.length)return;
let raf=0,tx=0,ty=0,cx=0,cy=0;
const apply=()=>{
  raf=0;
  cx+=(tx-cx)*0.12;
  cy+=(ty-cy)*0.12;
  const x=(cy*2.2).toFixed(3)+'deg';
  const y=(cx*2.8).toFixed(3)+'deg';
  cards.forEach(card=>{card.style.setProperty('--parallax-x',x);card.style.setProperty('--parallax-y',y);});
  if(Math.abs(tx-cx)>.001||Math.abs(ty-cy)>.001)raf=requestAnimationFrame(apply);
};
const move=(clientX,clientY)=>{
  const r=stage.getBoundingClientRect();
  tx=Math.max(-1,Math.min(1,(clientX-(r.left+r.width/2))/(r.width/2)));
  ty=Math.max(-1,Math.min(1,(clientY-(r.top+r.height/2))/(r.height/2)));
  if(!raf)raf=requestAnimationFrame(apply);
};
stage.addEventListener('pointermove',e=>move(e.clientX,e.clientY),{passive:true});
stage.addEventListener('pointerleave',()=>{tx=0;ty=0;if(!raf)raf=requestAnimationFrame(apply)},{passive:true});
})();
