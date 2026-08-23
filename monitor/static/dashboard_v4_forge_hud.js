(()=>{
'use strict';
if(window.__FIXEDCOIN_FORGE_HUD_V1__)return;
window.__FIXEDCOIN_FORGE_HUD_V1__=true;
const value=document.getElementById('poolDiffValue');
const label=document.getElementById('poolDiffLabel');
if(!value)return;
const fmt=n=>{n=Number(n)||0;if(n>=1e9)return(n/1e9).toFixed(2)+'B';if(n>=1e6)return(n/1e6).toFixed(2)+'M';if(n>=1e3)return(n/1e3).toFixed(2)+'K';return n.toFixed(n<10?2:0)};
let busy=false;
async function syncPoolDiff(){
  if(busy)return;
  busy=true;
  try{
    const r=await fetch('/api/status?ts='+Date.now(),{cache:'no-store'});
    if(!r.ok)return;
    const s=await r.json();
    const m=s.mining||{};
    const workers=m.workers||{};
    const first=Object.values(workers).find(w=>w&&w.active&&Number(w.difficulty)>0);
    const diff=Number(m.pool_difficulty||first?.difficulty||m.fixed_difficulty||0);
    value.textContent=fmt(diff);
    if(label)label.textContent=(m.vardiff_mode?'POOL DIFF · LIVE':'POOL DIFF · FIXED');
  }catch(_){
    if(label)label.textContent='POOL DIFF · OFFLINE';
  }finally{busy=false}
}
syncPoolDiff();
window.setInterval(syncPoolDiff,3000);
})();
