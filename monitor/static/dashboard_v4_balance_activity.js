(()=>{
'use strict';
if(window.__FIXEDCOIN_DASH_BALANCE_ACTIVITY__)return;
window.__FIXEDCOIN_DASH_BALANCE_ACTIVITY__=true;

const $=id=>document.getElementById(id);
const fmtCoin=v=>{
  const n=Number(v);
  if(!Number.isFinite(n)) return '—';
  return n.toFixed(8).replace(/0+$/,'').replace(/\.$/,'') || '0';
};
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const shortWork=msg=>{
  const m=String(msg||'').match(/(?:work|share_diff|diff)\s*[=:]\s*([0-9.]+)/i);
  if(!m)return '';
  const n=Number(m[1]);
  if(!Number.isFinite(n))return '';
  if(n>=1e9)return (n/1e9).toFixed(2)+'B';
  if(n>=1e6)return (n/1e6).toFixed(2)+'M';
  if(n>=1e3)return (n/1e3).toFixed(2)+'K';
  return n.toFixed(2);
};
const clock=v=>String(v||'').slice(11,19);

function setBalance(id,value){
  const el=$(id);
  if(el)el.textContent=Number.isFinite(Number(value))?fmtCoin(value)+' FIX':'—';
}

function renderBalance(s){
  const w=s?.wallet||{};
  const confirmed=Number(w.confirmed);
  const pending=Number(w.pending);
  const immature=Number(w.immature);
  // These are deliberately separate: immature is NOT folded into unconfirmed.
  const total=(Number.isFinite(confirmed)?confirmed:0)
             +(Number.isFinite(pending)?pending:0)
             +(Number.isFinite(immature)?immature:0);
  setBalance('balanceConfirmed',confirmed);
  setBalance('balanceUnconfirmed',pending);
  setBalance('balanceImmature',immature);
  setBalance('balanceTotal',total);
}

function classify(e){
  const msg=String(e?.message||'');
  if(/ACCEPT\s+#/i.test(msg))return {type:'accept',label:'ACCEPTED SHARE',value:shortWork(msg),icon:'✓'};
  if(/\bREJECT\b|LOW DIFF|stale job|bad params|invalid/i.test(msg))return {type:'reject',label:/LOW DIFF/i.test(msg)?'REJECTED (LOW DIFF)':'REJECTED SHARE',value:shortWork(msg),icon:'×'};
  if(/NEW ROUND/i.test(msg)){
    const m=msg.match(/height=(\d+)/i);
    return {type:'round',label:'ROUND STARTED',value:m?'#'+Number(m[1]).toLocaleString():'',icon:'⚑'};
  }
  if(/\bBLOCK\b/i.test(msg))return {type:'block',label:'BLOCK EVENT',value:'',icon:'◆'};
  return null;
}

let lastActivitySignature='';
async function refreshActivity(){
  try{
    const r=await fetch('/api/logs?ts='+Date.now(),{cache:'no-store'});
    if(!r.ok)return;
    const data=await r.json();
    const events=Array.isArray(data.events)?data.events:[];
    const rows=[];
    const seen=new Set();
    for(let i=events.length-1;i>=0&&rows.length<20;i--){
      const e=events[i], parsed=classify(e);
      if(!parsed)continue;
      const key=String(e.ts||'')+'|'+String(e.message||'');
      if(seen.has(key))continue;
      seen.add(key);
      rows.push({...parsed,time:clock(e.ts),raw:String(e.message||'')});
    }
    const sig=rows.map(x=>x.type+'|'+x.label+'|'+x.value+'|'+x.time+'|'+x.raw).join('\n');
    if(sig===lastActivitySignature)return;
    lastActivitySignature=sig;
    const host=$('activityList');
    if(!host)return;
    if(!rows.length){host.innerHTML='<div class="activity-empty">Waiting for live shares…</div>';return;}
    host.innerHTML=rows.slice(0,12).map(x=>`<div class="activity-row live-activity"><b class="${x.type==='accept'?'ok':x.type==='reject'?'bad':x.type==='block'?'block':'round'}">${x.icon}</b><span>${esc(x.label)}<br><small>${esc(x.value||'')}</small></span><time>${esc(x.time)}</time></div>`).join('');
  }catch(_){/* dashboard remains usable if the log endpoint is temporarily unavailable */}
}

let statusBusy=false;
async function refreshBalance(){
  if(statusBusy)return;
  statusBusy=true;
  try{
    const r=await fetch('/api/status?ts='+Date.now(),{cache:'no-store'});
    if(r.ok)renderBalance(await r.json());
  }catch(_){/* ignore transient dashboard/network errors */}
  finally{statusBusy=false;}
}

refreshActivity();
refreshBalance();
window.setInterval(refreshActivity,2000);
window.setInterval(refreshBalance,3000);
})();
