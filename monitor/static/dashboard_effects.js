(()=>{
'use strict';
if(window.__FIXEDCOIN_REALTIME_EFFECTS__) return;
window.__FIXEDCOIN_REALTIME_EFFECTS__=true;
const s=document.createElement('script');
s.src='/static/dashboard_realtime.js?v=20260823';
s.async=true;
s.onload=()=>console.info('[dashboard] realtime miner effects online');
s.onerror=()=>console.warn('[dashboard] realtime miner effects failed to load');
document.head.appendChild(s);
})();
