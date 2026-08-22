(()=>{
'use strict';
if(window.__FIXEDCOIN_REALTIME_EFFECTS__) return;
window.__FIXEDCOIN_REALTIME_EFFECTS__=true;
const s=document.createElement('script');
s.src='/static/dashboard_realtime_v2.js?v=20260823-v2';
s.async=true;
s.onload=()=>console.info('[dashboard] realtime 3D miner effects online');
s.onerror=()=>console.warn('[dashboard] realtime 3D miner effects failed to load');
document.head.appendChild(s);
})();
