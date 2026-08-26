(()=>{
'use strict';
if(window.__FIXEDCOIN_REFERENCE_FINAL__) return;
window.__FIXEDCOIN_REFERENCE_FINAL__=true;
const $=id=>document.getElementById(id);
const heightFmt=v=>{const n=Math.trunc(Number(v)||0);return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g,",")};
const fmtCoin=v=>{const n=Number(v);return Number.isFinite(n)?n.toFixed(8)+' FIX':'—'};
const fmtDiff=v=>{const n=Number(v)||0;if(n>=1e9)return(n/1e9).toFixed(2)+'B';if(n>=1e6)return(n/1e6).toFixed(2)+'M';if(n>=1e3)return(n/1e3).toFixed(2)+'K';return n.toFixed(2)};
const fmtDuration=sec=>{sec=Math.max(0,Math.floor(Number(sec)||0));const d=Math.floor(sec/86400),h=Math.floor(sec%86400/3600),m=Math.floor(sec%3600/60);if(d)return`~${d}d ${String(h).padStart(2,'0')}h`;return`${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec%60).padStart(2,'0')}`};
async function syncReferenceTelemetry(){try{const r=await fetch('/api/status?reference='+Date.now(),{cache:'no-store'});if(!r.ok)return;const s=await r.json(),w=s.wallet||{},m=s.mining||{},n=s.node||{},shares=Array.isArray(s.shares)?s.shares:[],now=Date.now()/1000,recent=shares.filter(x=>Number(x?.epoch)>0&&now-Number(x.epoch)>=0&&now-Number(x.epoch)<=600&&Number(x?.work||0)>0);const avg=recent.length?recent.reduce((a,x)=>a+Number(x.work||0),0)/recent.length:0;const oldest=recent.length?Number(recent[0]?.epoch||0):0;const newest=recent.length?Number(recent.at(-1)?.epoch||0):0;const sharesPerMin=(newest>oldest)?recent.length/(Math.max(1,newest-oldest)/60):0;const hs=Number(m.hashrate_5m)||0,diff=Number(n.difficulty||s.round?.difficulty||0),eta=hs>0&&diff>0?diff*4294967296/hs:0;const vals={confirmedBalance:fmtCoin(w.confirmed),unconfirmedBalance:fmtCoin(w.unconfirmed),immatureBalance:fmtCoin(w.immature),totalBalance:fmtCoin(w.total),liveVarDiff:fmtDiff(Object.values(m.workers||{}).reduce((d,x)=>Math.max(d,Number(x?.difficulty)||0),Number(m.fixed_difficulty)||0)),avgDiff:fmtDiff(avg),sharesMin:sharesPerMin.toFixed(1),eta:eta?fmtDuration(eta):'—'};Object.entries(vals).forEach(([id,value])=>{const el=$(id);if(el)el.textContent=value})}catch(_){} }
syncReferenceTelemetry();setInterval(syncReferenceTelemetry,3000);

const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
const surfaces=[...document.querySelectorAll('.parallax-card')],stage=$('forgeStage');let raf=0,px=0,py=0;
function paintParallax(){raf=0;surfaces.forEach((el,i)=>{const depth=(i%2?1:.82);el.style.setProperty('--rf-x',(px*depth).toFixed(2)+'deg');el.style.setProperty('--rf-y',(py*depth).toFixed(2)+'deg');el.style.transform=`perspective(900px) rotateY(calc(${el.classList.contains('rejected')?'-18deg':'8deg'} + var(--rf-x,0deg))) rotateX(calc(2deg + var(--rf-y,0deg))) translateZ(${Math.abs(px+py)*.12}px)`});if(stage){stage.style.setProperty('--scene-x',(px*.55).toFixed(2)+'px');stage.style.setProperty('--scene-y',(py*.55).toFixed(2)+'px')}}
function pointerMove(e){const r=(e.currentTarget||document.body).getBoundingClientRect(),x=clamp((e.clientX-r.left)/r.width,0,1),y=clamp((e.clientY-r.top)/r.height,0,1);px=(x-.5)*10;py=(.5-y)*8;if(!raf)raf=requestAnimationFrame(paintParallax)}
function resetParallax(){px=py=0;if(!raf)raf=requestAnimationFrame(paintParallax)}
if(stage){stage.addEventListener('pointermove',pointerMove,{passive:true});stage.addEventListener('pointerleave',resetParallax,{passive:true})}

/* Lightweight event-driven feedback. No canvas particle renderer or per-frame particle loop. */
const realtimeStyle=document.createElement('style');
realtimeStyle.textContent=`
.reference-dashboard .forge-counter.share-hit{animation:rfShareCard .72s cubic-bezier(.16,.84,.22,1)}
.reference-dashboard .combo.share-hit{animation:rfComboHit .72s cubic-bezier(.16,.84,.22,1)}
.reference-dashboard .share-burst{position:absolute;left:50%;top:50%;z-index:26;pointer-events:none;color:var(--rf-green);font:800 10px/1 var(--rf-mono);letter-spacing:.16em;text-shadow:0 0 10px rgba(77,255,114,.9);transform:translate(-50%,-50%);animation:rfShareBurst .78s cubic-bezier(.16,.84,.22,1) forwards}
.reference-dashboard .share-burst.reject{color:var(--rf-red);text-shadow:0 0 10px rgba(255,79,97,.9)}
.reference-dashboard .balance-card:nth-child(4){border-color:rgba(77,255,114,.38)!important;box-shadow:0 0 0 1px rgba(77,255,114,.06) inset,0 0 28px rgba(77,255,114,.06),0 24px 80px rgba(0,0,0,.48)!important}
.reference-dashboard .balance-card:nth-child(5){border-color:rgba(27,228,255,.32)!important}
@keyframes rfShareCard{0%{transform:perspective(900px) rotateY(8deg) rotateX(2deg) translateZ(0) scale(1)}24%{transform:perspective(900px) rotateY(8deg) rotateX(2deg) translateZ(18px) scale(1.045);box-shadow:inset 0 0 0 1px rgba(77,255,114,.2),0 0 32px rgba(77,255,114,.38),0 20px 45px rgba(0,0,0,.7)}100%{transform:perspective(900px) rotateY(8deg) rotateX(2deg) translateZ(0) scale(1)}}
@keyframes rfComboHit{0%,100%{transform:translateZ(45px) scale(1)}28%{transform:translateZ(75px) scale(1.12);filter:drop-shadow(0 0 14px rgba(255,181,47,.55))}55%{transform:translateZ(55px) scale(1.03)}}
@keyframes rfShareBurst{0%{opacity:0;transform:translate(-50%,-50%) scale(.65)}18%{opacity:1}100%{opacity:0;transform:translate(-50%,-115px) scale(1.12)}}
@media(prefers-reduced-motion:reduce){.reference-dashboard .share-burst,.reference-dashboard .forge-counter.share-hit,.reference-dashboard .combo.share-hit{animation:none!important}}
`;
document.head.appendChild(realtimeStyle);

const core=$('forgeCore'),acceptedCard=$('acceptedCounter'),rejectedCard=$('rejectedCounter'),combo=$('combo');
let shareTimer=0;
const hitCard=(el,kind)=>{if(!el)return;el.classList.remove('share-hit');void el.offsetWidth;el.classList.add('share-hit');clearTimeout(shareTimer);shareTimer=setTimeout(()=>el.classList.remove('share-hit'),760);if(stage){const burst=document.createElement('span');burst.className='share-burst'+(kind==='reject'?' reject':'');burst.textContent=kind==='reject'?'REJECT':'ACCEPT +1';stage.appendChild(burst);setTimeout(()=>burst.remove(),820)}};
const handleLiveEvent=d=>{if(!d||!d.type)return;if(d.type==='accept'){hitCard(acceptedCard,'accept');hitCard(combo,'accept')}else if(d.type==='reject'){hitCard(rejectedCard,'reject')}window.dispatchEvent(new CustomEvent('fixedcoin:live',{detail:d}))};
if(core){core.addEventListener('pointerenter',()=>core.classList.add('core-hot'),{passive:true});core.addEventListener('pointerleave',()=>core.classList.remove('core-hot'),{passive:true});try{const es=new EventSource('/api/stream');es.onmessage=e=>{try{handleLiveEvent(JSON.parse(e.data||'{}'))}catch(_){}};es.onerror=()=>{}}catch(_){} }
document.documentElement.dataset.fixedcoinReference='final';
})();
