(()=>{
'use strict';
if(window.__FIXEDCOIN_FORGE_V1__)return;window.__FIXEDCOIN_FORGE_V1__=true;
const forge=document.getElementById('forge');
const core=document.getElementById('forgeCore');
if(!forge||!core)return;
let lastAccept=Number(document.getElementById('acceptedCount')?.textContent)||0;
let lastReject=Number(document.getElementById('rejectedCount')?.textContent)||0;
let booted=false;
const pulse=(kind,ms=760)=>{forge.classList.remove('hit-accept','hit-reject','hit-block','hit-round');void forge.offsetWidth;forge.classList.add(kind);window.setTimeout(()=>forge.classList.remove(kind),ms)};
const spawnDust=(kind)=>{
  const host=document.getElementById('forgeParticleField')||forge;
  for(let i=0;i<(kind==='reject'?16:28);i++){
    const p=document.createElement('i');p.className='forge-dust '+(kind==='reject'?'red':'green');
    p.style.setProperty('--dx',`${(Math.random()-.5)*260}px`);p.style.setProperty('--dy',`${(Math.random()-.5)*180}px`);p.style.setProperty('--delay',`${Math.random()*90}ms`);host.appendChild(p);
    p.addEventListener('animationend',()=>p.remove(),{once:true});
  }
};
function accept(){pulse('hit-accept',760);spawnDust('accept')}
function reject(){pulse('hit-reject',620);spawnDust('reject')}
function block(){pulse('hit-block',1600);spawnDust('accept')}
function round(){pulse('hit-round',1100)}
window.addEventListener('fixedcoin:accept',accept);
window.addEventListener('fixedcoin:reject',reject);
window.addEventListener('fixedcoin:block',block);
window.addEventListener('fixedcoin:round',round);
const observer=new MutationObserver(()=>{
 const a=Number(document.getElementById('acceptedCount')?.textContent)||0;
 const r=Number(document.getElementById('rejectedCount')?.textContent)||0;
 if(booted){if(a>lastAccept)accept();if(r>lastReject)reject()}
 lastAccept=a;lastReject=r;booted=true;
});
observer.observe(document.getElementById('acceptedCount'),{childList:true,characterData:true,subtree:true});
observer.observe(document.getElementById('rejectedCount'),{childList:true,characterData:true,subtree:true});
// Low-rate autonomous micro-particles keep the core alive between real events.
const field=document.getElementById('forgeParticleField');
if(field)setInterval(()=>{const p=document.createElement('i');p.className='forge-dust ambient-dust';p.style.left=(42+Math.random()*18)+'%';p.style.top=(36+Math.random()*30)+'%';p.style.setProperty('--dx',`${(Math.random()-.5)*90}px`);p.style.setProperty('--dy',`${-30-Math.random()*100}px`);field.appendChild(p);setTimeout(()=>p.remove(),2200)},420);
})();
