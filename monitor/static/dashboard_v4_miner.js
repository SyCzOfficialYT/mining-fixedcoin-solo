(()=>{'use strict';
if(window.__FIXEDCOIN_MINER_PUPPET_V2__)return;window.__FIXEDCOIN_MINER_PUPPET_V2__=true;
const host=document.getElementById('minerFigure');
if(!host)return;

/*
 * FIX-ASIC FORGE / V2
 *
 * This is intentionally NOT an image wrapper. The reference miner is rebuilt
 * from vector parts so the helmet, torso, shoulders, upper arm, forearm,
 * hand, hammer, legs and boots can move independently like a small humanoid
 * rig. No <img>, <image>, canvas screenshot or raster reference is used.
 */
const svg=`<svg class="miner-puppet" viewBox="0 0 430 430" preserveAspectRatio="xMidYMax meet" role="img" aria-label="FIX-ASIC miner forging FixedCoin">
<defs>
 <linearGradient id="mSteel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#668994"/><stop offset=".28" stop-color="#385762"/><stop offset=".65" stop-color="#132b35"/><stop offset="1" stop-color="#061116"/></linearGradient>
 <linearGradient id="mSteel2" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#8baab2"/><stop offset=".35" stop-color="#42646e"/><stop offset="1" stop-color="#0a171d"/></linearGradient>
 <linearGradient id="mDark" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#173743"/><stop offset=".5" stop-color="#08161d"/><stop offset="1" stop-color="#02080c"/></linearGradient>
 <linearGradient id="mCyan" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#0c7c94"/><stop offset=".45" stop-color="#36edff"/><stop offset="1" stop-color="#0b7389"/></linearGradient>
 <linearGradient id="mHammer" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#173a48"/><stop offset=".25" stop-color="#5dc3d6"/><stop offset=".55" stop-color="#d5edf0"/><stop offset="1" stop-color="#566f77"/></linearGradient>
 <radialGradient id="mLens"><stop stop-color="#fffbd0"/><stop offset=".16" stop-color="#8effff"/><stop offset=".45" stop-color="#21dff3"/><stop offset="1" stop-color="#087185" stop-opacity="0"/></radialGradient>
 <radialGradient id="mChestGlow"><stop stop-color="#28f2ff" stop-opacity=".75"/><stop offset="1" stop-color="#28f2ff" stop-opacity="0"/></radialGradient>
 <filter id="mGlow"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <filter id="mSoftGlow"><feGaussianBlur stdDeviation="9"/></filter>
 <filter id="mShadow"><feDropShadow dx="0" dy="15" stdDeviation="12" flood-color="#000" flood-opacity=".65"/></filter>
 <linearGradient id="mVisor" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#132d37"/><stop offset=".5" stop-color="#02090d"/><stop offset="1" stop-color="#0d222b"/></linearGradient>
</defs>
<g class="miner-rig" filter="url(#mShadow)">
 <ellipse class="miner-shadow" cx="211" cy="407" rx="148" ry="15" fill="#000" opacity=".65"/>
 <g class="miner-backpack"><path d="M75 160Q42 165 42 204V298Q42 318 60 325L92 318V177Z" fill="url(#mDark)" stroke="#315863" stroke-width="5"/><path d="M59 187V294M73 178V302" stroke="#173c48" stroke-width="8" stroke-linecap="round"/></g>
 <g class="miner-legs"><g class="miner-leg miner-leg-l"><path d="M117 303L170 303L166 375L153 394H111L118 370Z" fill="url(#mSteel)" stroke="#63838d" stroke-width="5"/><path d="M104 387H158Q170 387 177 401L172 411H92Q90 397 104 387Z" fill="#071319" stroke="#54747e" stroke-width="5"/></g><g class="miner-leg miner-leg-r"><path d="M181 303L232 302L241 371L259 390L250 408H180L176 392L190 371Z" fill="url(#mSteel)" stroke="#63838d" stroke-width="5"/><path d="M222 386H273Q286 388 292 401L287 411H212Q210 397 222 386Z" fill="#071319" stroke="#54747e" stroke-width="5"/></g></g>
 <g class="miner-torso"><path d="M105 148Q118 125 151 120H211Q247 125 263 151L277 291Q259 315 213 320H151Q108 314 93 290Z" fill="url(#mSteel)" stroke="#6e929b" stroke-width="6"/><path d="M112 171Q175 191 258 168L265 280Q229 299 145 286Z" fill="#061319" opacity=".72"/><path d="M123 183H253M119 214H258M121 247H260" stroke="#1d4c59" stroke-width="4" opacity=".85"/><ellipse cx="182" cy="212" rx="75" ry="70" fill="url(#mChestGlow)" opacity=".16"/><text x="177" y="232" text-anchor="middle" fill="#cbe5e9" font-family="JetBrains Mono,monospace" font-size="17" font-weight="700" letter-spacing="3">FIX-ASIC</text><rect x="143" y="261" width="78" height="7" rx="4" fill="url(#mCyan)" filter="url(#mGlow)"/><path d="M111 157L100 177M252 155L267 176" stroke="#8aaab1" stroke-width="5"/></g>
 <g class="miner-head"><path d="M103 111Q99 70 122 43Q145 17 184 17Q225 17 248 44Q269 70 264 113L247 144H119Z" fill="url(#mDark)" stroke="#6e929b" stroke-width="6"/><path d="M94 63Q108 25 151 12Q198 -1 236 22Q261 38 273 67L262 92Q220 68 178 69Q133 69 98 90Z" fill="url(#mSteel2)" stroke="#7799a1" stroke-width="6"/><path d="M111 89Q177 70 255 91L249 126Q224 148 181 148Q139 146 116 125Z" fill="url(#mVisor)" stroke="#446872" stroke-width="5"/><path d="M128 117Q180 105 236 117" stroke="#20e4f4" stroke-width="5" stroke-linecap="round" filter="url(#mGlow)"/><circle cx="181" cy="49" r="28" fill="url(#mLens)"/><circle cx="181" cy="49" r="10" fill="#fff4b0" filter="url(#mGlow)"/><path d="M118 145Q180 159 250 145" stroke="#8aaab1" stroke-width="5"/></g>
 <g class="miner-arm-back"><path d="M111 161Q84 166 78 194L71 277Q74 302 98 310Q117 307 124 284L135 200Z" fill="url(#mSteel2)" stroke="#63848d" stroke-width="6"/><path d="M94 191L88 270" stroke="#1c4955" stroke-width="8" stroke-linecap="round"/></g>
 <g class="hammer-rig">
   <g class="miner-upper-arm"><path d="M226 159Q247 151 266 164L305 194L284 228Q263 210 241 199L219 188Z" fill="url(#mSteel2)" stroke="#71939c" stroke-width="6"/></g>
   <g class="miner-forearm"><path d="M289 194L332 210L322 245L276 225Z" fill="url(#mSteel)" stroke="#71939c" stroke-width="6"/><path d="M316 212L337 217L329 242L309 237Z" fill="#4c6e77" stroke="#7d9da5" stroke-width="4"/></g>
   <g class="miner-hammer"><rect x="322" y="219" width="92" height="13" rx="6" fill="url(#mHammer)"/><path d="M389 190L421 198Q429 201 428 211L424 246Q422 255 413 254L385 247L390 231Z" fill="url(#mSteel2)" stroke="#a1bec4" stroke-width="5"/><path d="M397 202L422 208" stroke="#d6f2f4" stroke-width="4" opacity=".6"/></g>
 </g>
 <g class="miner-shoulder"><circle cx="229" cy="174" r="19" fill="#456873" stroke="#7d9da5" stroke-width="5"/></g>
 <g class="miner-antenna"><path d="M247 54V20" stroke="#5d8790" stroke-width="4"/><circle cx="247" cy="16" r="6" fill="#51f77b" filter="url(#mGlow)"/></g>
</g>
<g class="miner-idle-glow" opacity=".6"><ellipse cx="182" cy="138" rx="125" ry="105" fill="url(#mChestGlow)" filter="url(#mSoftGlow)"/></g>
</svg>`;
host.innerHTML=svg;

const puppet=host.querySelector('.miner-puppet');
const rig=host.querySelector('.miner-rig');
const torso=host.querySelector('.miner-torso');
const head=host.querySelector('.miner-head');
const upper=host.querySelector('.miner-upper-arm');
const fore=host.querySelector('.miner-forearm');
const hammer=host.querySelector('.miner-hammer');
const legs=host.querySelector('.miner-legs');
const lens=host.querySelector('.miner-head circle');
const shoulder=host.querySelector('.miner-shoulder');

for(const el of [rig,torso,head,upper,fore,hammer,legs,shoulder]){
 if(el){el.style.transformBox='fill-box';el.style.transformOrigin='center';}
}
if(upper)upper.style.transformOrigin='12% 50%';
if(fore)fore.style.transformOrigin='15% 50%';
if(hammer)hammer.style.transformOrigin='8% 50%';
if(shoulder)shoulder.style.transformOrigin='50% 50%';

let strikeToken=0;
let idleAnims=[];
function clearIdle(){idleAnims.forEach(a=>{try{a.cancel()}catch(_){}});idleAnims=[]}
function playIdle(){
 if(window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
 clearIdle();
 const opt={duration:2600,easing:'ease-in-out',iterations:Infinity,fill:'both'};
 idleAnims.push(rig.animate([{transform:'translateY(0)'},{transform:'translateY(-2px)'},{transform:'translateY(0)'}],opt));
 idleAnims.push(head.animate([{transform:'rotate(-.6deg)'},{transform:'rotate(.8deg)'},{transform:'rotate(-.6deg)'}],{...opt,duration:3400}));
 idleAnims.push(shoulder.animate([{transform:'translateY(0)'},{transform:'translateY(1px)'},{transform:'translateY(0)'}],{...opt,duration:2100}));
}
playIdle();

function impactFlash(){
 const g=document.createElementNS('http://www.w3.org/2000/svg','g');
 g.setAttribute('class','svg-impact');g.setAttribute('transform','translate(405 246)');
 g.innerHTML='<circle r="7" fill="#fff6b0"/><circle r="18" fill="none" stroke="#ffd16b" stroke-width="3"/><circle r="34" fill="none" stroke="#ff7138" stroke-width="2" opacity=".8"/><path d="M-42 0H-20M20 0H42M0-42V-20M0 20V42" stroke="#ffe7a0" stroke-width="3" stroke-linecap="round"/>';
 puppet.appendChild(g);
 g.animate([{opacity:0,transform:'translate(405px,246px) scale(.2)'},{opacity:1,transform:'translate(405px,246px) scale(1.15)',offset:.22},{opacity:0,transform:'translate(405px,246px) scale(2.4)'}],{duration:380,easing:'cubic-bezier(.1,.8,.2,1)'}).finished.finally(()=>g.remove()).catch(()=>g.remove());
}

function strike(kind='accept'){
 const token=++strikeToken;
 clearIdle();
 const accept=kind==='accept';
 const duration=accept?980:640;
 const ease='cubic-bezier(.12,.82,.18,1)';
 const animations=[];
 animations.push(rig.animate(accept?[
   {transform:'translate(0,0) rotate(0deg)',offset:0},{transform:'translate(-3px,2px) rotate(-1deg)',offset:.18},{transform:'translate(-9px,7px) rotate(-4deg)',offset:.42},{transform:'translate(5px,4px) rotate(2deg)',offset:.58},{transform:'translate(1px,1px) rotate(.5deg)',offset:.76},{transform:'translate(0,0) rotate(0deg)'}
 ]:[{transform:'translate(0,0)'},{transform:'translate(-2px,1px)'},{transform:'translate(2px,1px)'},{transform:'translate(0,0)'}],{duration,easing:ease,fill:'both'}));
 animations.push(torso.animate(accept?[
   {transform:'rotate(0deg)'},{transform:'rotate(-2.5deg)',offset:.38},{transform:'rotate(3deg)',offset:.59},{transform:'rotate(0deg)'}
 ]:[{transform:'rotate(0)'},{transform:'rotate(-1deg)',offset:.35},{transform:'rotate(1deg)',offset:.62},{transform:'rotate(0)'}],{duration,easing:ease,fill:'both'}));
 animations.push(upper.animate(accept?[
   {transform:'rotate(4deg)' ,offset:0},{transform:'rotate(-35deg) translate(-3px,-4px)',offset:.27},{transform:'rotate(-61deg) translate(-4px,-7px)',offset:.42},{transform:'rotate(24deg) translate(7px,7px)',offset:.59},{transform:'rotate(8deg)',offset:.76},{transform:'rotate(4deg)'}
 ]:[{transform:'rotate(4deg)'},{transform:'rotate(-10deg)',offset:.3},{transform:'rotate(9deg)',offset:.6},{transform:'rotate(4deg)'}],{duration,easing:ease,fill:'both'}));
 animations.push(fore.animate(accept?[
   {transform:'rotate(2deg)' ,offset:0},{transform:'rotate(-15deg)',offset:.25},{transform:'rotate(-40deg)',offset:.43},{transform:'rotate(42deg) translate(8px,8px)',offset:.58},{transform:'rotate(14deg)',offset:.76},{transform:'rotate(2deg)'}
 ]:[{transform:'rotate(2deg)'},{transform:'rotate(-8deg)',offset:.3},{transform:'rotate(10deg)',offset:.62},{transform:'rotate(2deg)'}],{duration,easing:ease,fill:'both'}));
 animations.push(hammer.animate(accept?[
   {transform:'rotate(8deg)',offset:0},{transform:'rotate(-20deg)',offset:.25},{transform:'rotate(-48deg)',offset:.42},{transform:'rotate(30deg)',offset:.55},{transform:'rotate(12deg)',offset:.7},{transform:'rotate(8deg)'}
 ]:[{transform:'rotate(8deg)'},{transform:'rotate(-12deg)',offset:.32},{transform:'rotate(15deg)',offset:.62},{transform:'rotate(8deg)'}],{duration,easing:ease,fill:'both'}));
 animations.push(legs.animate(accept?[
   {transform:'translateY(0)'},{transform:'translateY(2px) rotate(-.5deg)',offset:.45},{transform:'translateY(1px) rotate(.4deg)',offset:.62},{transform:'translateY(0)'}
 ]:[{transform:'translateY(0)'},{transform:'translateY(1px)'},{transform:'translateY(0)'}],{duration,easing:ease,fill:'both'}));
 if(accept){
   setTimeout(()=>{if(token===strikeToken)impactFlash()},Math.round(duration*.54));
   setTimeout(()=>emitImpactParticles('accept'),Math.round(duration*.50));
 }
 Promise.all(animations.map(a=>a.finished.catch(()=>null))).finally(()=>{if(token===strikeToken)playIdle()});
}

/* Forge particles: one rAF loop, multiple physical layers (sparks, embers, dust, trails). */
const stage=document.getElementById('forgeStage');
const canvas=document.createElement('canvas');canvas.className='miner-particle-canvas';stage.appendChild(canvas);
const ctx=canvas.getContext('2d',{alpha:true});let dpr=1,particles=[],raf=0,last=performance.now();
function resize(){const r=stage.getBoundingClientRect();dpr=Math.min(2,window.devicePixelRatio||1);canvas.width=Math.max(1,Math.round(r.width*dpr));canvas.height=Math.max(1,Math.round(r.height*dpr));canvas.style.width=r.width+'px';canvas.style.height=r.height+'px';ctx.setTransform(dpr,0,0,dpr,0,0)}
function point(el){if(!el)return null;const a=el.getBoundingClientRect(),b=canvas.getBoundingClientRect();return{x:a.left+a.width*.5-b.left,y:a.top+a.height*.5-b.top}}
function spawn(from,to,kind,count){const a=point(from),b=point(to);if(!a||!b)return;for(let i=0;i<count;i++){const dx=b.x-a.x,dy=b.y-a.y,dist=Math.hypot(dx,dy),ang=Math.atan2(dy,dx)+(Math.random()-.5)*.38, speed=dist*(.0015+Math.random()*.002);particles.push({x:a.x+(Math.random()-.5)*18,y:a.y+(Math.random()-.5)*12,vx:Math.cos(ang)*speed,vy:Math.sin(ang)*speed-(Math.random()*.12),life:0,max:650+Math.random()*850,size:1.2+Math.random()*3.6,kind,trail:[],rot:Math.random()*6.28,spin:(Math.random()-.5)*.12,gravity:.00045+Math.random()*.0005})}}
function emitImpactParticles(kind){const from=document.querySelector('.svg-impact')||document.getElementById('anvil');const to=document.getElementById(kind==='reject'?'rejectedCounter':'acceptedCounter');spawn(from,to,kind,kind==='reject'?26:52);if(!raf)raf=requestAnimationFrame(tick)}
function tick(now){const dt=Math.min(34,now-last);last=now;const r=canvas.getBoundingClientRect();ctx.clearRect(0,0,r.width,r.height);for(let i=particles.length-1;i>=0;i--){const p=particles[i];p.life+=dt;p.trail.unshift({x:p.x,y:p.y});if(p.trail.length>9)p.trail.pop();p.x+=p.vx*dt;p.y+=p.vy*dt;p.vx*=.998;p.vy+=p.gravity*dt;p.rot+=p.spin;const t=p.life/p.max,alpha=Math.sin(Math.min(1,t)*Math.PI),good=p.kind!=='reject',rgb=good?'80,255,112':'255,75,66';if(p.trail.length>1){ctx.beginPath();ctx.moveTo(p.trail[0].x,p.trail[0].y);for(let j=1;j<p.trail.length;j++)ctx.lineTo(p.trail[j].x,p.trail[j].y);ctx.strokeStyle=`rgba(${rgb},${alpha*.42})`;ctx.lineWidth=Math.max(.7,p.size*.65);ctx.stroke()}ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.rot);ctx.shadowBlur=15;ctx.shadowColor=`rgba(${rgb},${alpha})`;ctx.fillStyle=`rgba(235,255,225,${alpha})`;ctx.fillRect(-p.size*.5,-p.size*.5,p.size,p.size);ctx.restore();if(p.life>=p.max)particles.splice(i,1)}raf=particles.length?requestAnimationFrame(tick):0}
window.addEventListener('resize',resize,{passive:true});resize();

const timeEl=document.getElementById('timeRemain'),pctEl=document.getElementById('timePct'),statusEl=document.getElementById('roundStatus'),roundEl=document.getElementById('roundId');
let round={started:0,target:600,height:0};
function parseEpoch(v){if(!v)return 0;if(typeof v==='number')return v>1e12?v/1000:v;const n=Number(v);if(Number.isFinite(n)&&n>0)return n>1e12?n/1000:n;const t=Date.parse(String(v).replace(' ','T'));return Number.isFinite(t)?t/1000:0}
function paintTimer(){if(!timeEl)return;if(!round.started){timeEl.textContent='00:00';pctEl.textContent='0.0%';statusEl.textContent='WAITING';statusEl.className='status waiting';requestAnimationFrame(paintTimer);return}const now=Date.now()/1000,remain=Math.max(0,round.target-(now-round.started)),pct=Math.max(0,Math.min(100,remain/round.target*100)),sec=Math.floor(remain);timeEl.textContent=String(Math.floor(sec/60)).padStart(2,'0')+':'+String(sec%60).padStart(2,'0');pctEl.textContent=pct.toFixed(1)+'%';statusEl.textContent=remain>0?'ACTIVE':'WAITING';statusEl.className='status '+(remain>0?'active':'waiting');requestAnimationFrame(paintTimer)}
async function hydrate(){try{const r=await fetch('/api/status?ts='+Date.now(),{cache:'no-store'});if(!r.ok)return;const s=await r.json(),rr=s.round||{};round={started:parseEpoch(rr.started_epoch||rr.started_at),target:Number(rr.target_seconds)||600,height:Number(rr.height||0)};if(roundEl&&round.height)roundEl.textContent='#'+round.height.toLocaleString('en-US')}catch(_){}}
paintTimer();hydrate();

/* Only accept/reject/block/round events are consumed here. The authoritative
   SSE is already provided by dashboard_v4.js; no second EventSource is opened. */
window.addEventListener('fixedcoin:accept',()=>strike('accept'),{passive:true});
window.addEventListener('fixedcoin:reject',()=>strike('reject'),{passive:true});
window.addEventListener('fixedcoin:block',()=>{rig.animate([{transform:'scale(1)'},{transform:'scale(1.035) translateY(-5px)'},{transform:'scale(1)'}],{duration:900,easing:'cubic-bezier(.1,.9,.2,1)'});emitImpactParticles('accept')},{passive:true});
window.addEventListener('fixedcoin:round',e=>{const x=e.detail||{};const started=parseEpoch(x.started_epoch||x.started_at||x.ts);if(started)round={started,target:Number(x.target_seconds)||600,height:Number(x.height||0)};if(roundEl&&round.height)roundEl.textContent='#'+round.height.toLocaleString('en-US')},{passive:true});
})();
