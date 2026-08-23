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
function accept(){pulse('hit-accept',900)}
function reject(){pulse('hit-reject',820)}
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
