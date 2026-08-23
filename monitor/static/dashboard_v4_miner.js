(()=>{'use strict';
if(window.__FIXEDCOIN_MINER_PUPPET__)return;window.__FIXEDCOIN_MINER_PUPPET__=true;
const host=document.getElementById('minerFigure'); if(!host)return;
const src='/static/miner_reference.svg?v=20260823-2';
host.innerHTML=`<svg class="miner-puppet" viewBox="0 0 180 202" preserveAspectRatio="xMidYMid meet" aria-label="FIX-ASIC animated miner" role="img">
<defs>
 <clipPath id="minerBodyClip"><path fill-rule="evenodd" d="M0 0H180V202H0ZM92 72L108 75L124 88L139 96L156 88L179 80V132L163 149L143 151L128 137L111 126L98 112L91 98Z"/></clipPath>
 <clipPath id="minerArmClip"><path d="M88 72L108 75L124 88L139 96L156 88L179 80V132L163 149L143 151L128 137L111 126L98 112L91 98Z"/></clipPath>
 <filter id="minerGlow"><feGaussianBlur stdDeviation="2.8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<g class="miner-body-rig"><image href="${src}" width="180" height="202" preserveAspectRatio="xMidYMid meet" clip-path="url(#minerBodyClip)"/></g>
<g class="miner-arm-rig"><image href="${src}" width="180" height="202" preserveAspectRatio="xMidYMid meet" clip-path="url(#minerArmClip)"/></g>
<g class="miner-impact-flash" opacity="0"><circle cx="154" cy="132" r="5" fill="#fff3b0" filter="url(#minerGlow)"/><circle cx="154" cy="132" r="14" fill="none" stroke="#ffb642" stroke-width="1.5"/><circle cx="154" cy="132" r="25" fill="none" stroke="#ff7b32" stroke-width="1" opacity=".55"/></g>
</svg>`;
const body=host.querySelector('.miner-body-rig'),arm=host.querySelector('.miner-arm-rig'),flash=host.querySelector('.miner-impact-flash');
body.style.transformBox='view-box';body.style.transformOrigin='50% 86%';arm.style.transformBox='view-box';arm.style.transformOrigin='94px 84px';
let strikeAnim=null;
function strike(kind='accept'){
 if(strikeAnim)strikeAnim.cancel();
 const accept=kind==='accept',duration=accept?900:650;
 const kf=accept?[
  {transform:'rotate(0deg) translate3d(0,0,0)',offset:0},{transform:'rotate(-18deg) translate3d(-1px,-1px,0)',offset:.16},{transform:'rotate(-47deg) translate3d(-2px,-2px,0)',offset:.30},{transform:'rotate(-31deg) translate3d(0,0,0)',offset:.39},{transform:'rotate(22deg) translate3d(5px,5px,0)',offset:.56},{transform:'rotate(11deg) translate3d(3px,2px,0)',offset:.68},{transform:'rotate(0deg) translate3d(0,0,0)',offset:1}
 ]:[{transform:'rotate(0deg)'},{transform:'rotate(-10deg) translate3d(-2px,0,0)',offset:.3},{transform:'rotate(8deg) translate3d(2px,2px,0)',offset:.58},{transform:'rotate(0deg)'}];
 strikeAnim=arm.animate(kf,{duration,easing:'cubic-bezier(.15,.9,.16,1)',fill:'both'});
 body.animate(accept?[{transform:'translate3d(0,0,0) rotate(0deg)'},{transform:'translate3d(-2px,1px,0) rotate(-.7deg)',offset:.3},{transform:'translate3d(5px,4px,0) rotate(1.2deg)',offset:.57},{transform:'translate3d(0,0,0)'}]:[{transform:'translate3d(0,0,0)'},{transform:'translate3d(-2px,1px,0)',offset:.35},{transform:'translate3d(1px,0,0)'},{transform:'translate3d(0,0,0)'}],{duration,easing:'cubic-bezier(.2,.8,.2,1)',fill:'both'});
 if(accept)setTimeout(()=>{host.classList.add('puppet-impact');flash.animate([{opacity:0,transform:'scale(.2)'},{opacity:1,transform:'scale(1.1)',offset:.25},{opacity:0,transform:'scale(2.6)'}],{duration:320,easing:'cubic-bezier(.1,.8,.2,1)'}).finished.catch(()=>{});setTimeout(()=>host.classList.remove('puppet-impact'),340)},Math.round(duration*.54));
}
if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches)body.animate([{transform:'translateY(0)'},{transform:'translateY(-1.5px)',offset:.5},{transform:'translateY(0)'}],{duration:2600,easing:'ease-in-out',iterations:Infinity});
window.addEventListener('fixedcoin:accept',()=>strike('accept'),{passive:true});window.addEventListener('fixedcoin:reject',()=>strike('reject'),{passive:true});window.addEventListener('fixedcoin:block',()=>{host.classList.add('puppet-block');setTimeout(()=>host.classList.remove('puppet-block'),1200)},{passive:true});

const timeEl=document.getElementById('timeRemain'),pctEl=document.getElementById('timePct'),statusEl=document.getElementById('roundStatus'),roundEl=document.getElementById('roundId');
let round={started:0,target:600,height:0};
function parseEpoch(v){if(!v)return 0;if(typeof v==='number')return v>1e12?v/1000:v;const n=Number(v);if(Number.isFinite(n)&&n>0)return n>1e12?n/1000:n;const t=Date.parse(String(v).replace(' ','T'));return Number.isFinite(t)?t/1000:0}
function paintTimer(){if(!timeEl)return;if(!round.started){timeEl.textContent='00:00';pctEl.textContent='0.0%';statusEl.textContent='WAITING';statusEl.className='status waiting';return}const now=Date.now()/1000,remain=Math.max(0,round.target-(now-round.started)),pct=Math.max(0,Math.min(100,remain/round.target*100)),sec=Math.floor(remain);timeEl.textContent=String(Math.floor(sec/60)).padStart(2,'0')+':'+String(sec%60).padStart(2,'0');pctEl.textContent=pct.toFixed(1)+'%';statusEl.textContent=remain>0?'ACTIVE':'WAITING';statusEl.className='status '+(remain>0?'active':'waiting');requestAnimationFrame(paintTimer)}
async function hydrate(){try{const r=await fetch('/api/status?ts='+Date.now(),{cache:'no-store'});if(!r.ok)return;const s=await r.json(),rr=s.round||{};round={started:parseEpoch(rr.started_epoch||rr.started_at),target:Number(rr.target_seconds)||600,height:Number(rr.height||0)};if(roundEl&&round.height)roundEl.textContent='#'+round.height.toLocaleString('en-US')}catch(_){} }
paintTimer();hydrate();

const stage=document.getElementById('forgeStage');const pc=document.createElement('canvas');pc.className='miner-particle-canvas';stage.appendChild(pc);const ctx=pc.getContext('2d');let ps=[],last=performance.now(),running=false;
function resize(){const r=stage.getBoundingClientRect(),d=Math.min(2,devicePixelRatio||1);pc.width=Math.max(1,r.width*d);pc.height=Math.max(1,r.height*d);pc.style.width=r.width+'px';pc.style.height=r.height+'px';ctx.setTransform(d,0,0,d,0,0)}
function point(el){if(!el)return null;const a=el.getBoundingClientRect(),b=pc.getBoundingClientRect();return{x:a.left+a.width/2-b.left,y:a.top+a.height/2-b.top}}
function spawn(kind,count=38){const a=point(host.querySelector('.miner-impact-flash')),target=point(kind==='reject'?document.getElementById('rejectedCounter'):document.getElementById('acceptedCounter'));if(!a||!target)return;for(let i=0;i<count;i++){const ang=Math.atan2(target.y-a.y,target.x-a.x)+(Math.random()-.5)*.55,dist=Math.hypot(target.x-a.x,target.y-a.y),speed=dist*(.0015+Math.random()*.0018);ps.push({x:a.x+(Math.random()-.5)*20,y:a.y+(Math.random()-.5)*20,vx:Math.cos(ang)*speed,vy:Math.sin(ang)*speed-(Math.random()*.18),life:0,max:700+Math.random()*900,size:1.2+Math.random()*3.2,kind,rot:Math.random()*6.28,trail:[]})}if(!running){running=true;requestAnimationFrame(tick)}}
function tick(now){const dt=Math.min(32,now-last);last=now;const r=pc.getBoundingClientRect();ctx.clearRect(0,0,r.width,r.height);for(let i=ps.length-1;i>=0;i--){const p=ps[i];p.life+=dt;p.trail.unshift({x:p.x,y:p.y});if(p.trail.length>8)p.trail.pop();p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=.00018*dt;const alpha=Math.max(0,Math.sin(Math.min(1,p.life/p.max)*Math.PI)),good=p.kind!=='reject',rgb=good?'93,255,119':'255,73,65';if(p.trail.length>1){ctx.beginPath();ctx.moveTo(p.trail[0].x,p.trail[0].y);for(let j=1;j<p.trail.length;j++)ctx.lineTo(p.trail[j].x,p.trail[j].y);ctx.strokeStyle=`rgba(${rgb},${alpha*.35})`;ctx.lineWidth=Math.max(1,p.size*.7);ctx.stroke()}const g=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.size*5);g.addColorStop(0,`rgba(255,255,255,${alpha})`);g.addColorStop(.18,`rgba(${rgb},${alpha})`);g.addColorStop(1,`rgba(${rgb},0)`);ctx.fillStyle=g;ctx.beginPath();ctx.arc(p.x,p.y,p.size*5,0,Math.PI*2);ctx.fill();ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.rot+=.04);ctx.fillStyle=`rgba(220,255,226,${alpha})`;ctx.shadowBlur=12;ctx.shadowColor=`rgba(${rgb},${alpha})`;ctx.fillRect(-p.size/2,-p.size/2,p.size,p.size);ctx.restore();if(p.life>=p.max)ps.splice(i,1)}running=ps.length>0;if(running)requestAnimationFrame(tick)}
window.addEventListener('resize',resize,{passive:true});resize();
const stream=new EventSource('/api/stream');stream.onmessage=e=>{try{const x=JSON.parse(e.data||'{}');if(x.type==='accept'){window.dispatchEvent(new CustomEvent('fixedcoin:accept',{detail:x}));const combo=Number(document.getElementById('comboValue')?.textContent?.replace(/[^0-9]/g,'')||0);spawn('accept',Math.min(80,38+combo*4))}else if(x.type==='reject'){window.dispatchEvent(new CustomEvent('fixedcoin:reject',{detail:x}));spawn('reject',28)}else if(x.type==='round'){round={started:parseEpoch(x.ts),target:600,height:Number(x.height||0)};if(roundEl)roundEl.textContent='#'+round.height.toLocaleString('en-US')}else if(x.type==='block'){window.dispatchEvent(new CustomEvent('fixedcoin:block',{detail:x}))}}catch(_){}};
})();