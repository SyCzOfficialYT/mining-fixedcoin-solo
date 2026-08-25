(()=>{
'use strict';
if(window.__FIXEDCOIN_FORGE_V3__)return;
window.__FIXEDCOIN_FORGE_V3__=true;
const forge=document.getElementById('forge');
const core=document.getElementById('forgeCore');
if(!forge||!core)return;
let lastAccept=Number(document.getElementById('acceptedCount')?.textContent)||0;
let lastReject=Number(document.getElementById('rejectedCount')?.textContent)||0;
let booted=false;
const pulse=(kind,ms=900)=>{forge.classList.remove('hit-accept','hit-reject','hit-block','hit-round');void forge.offsetWidth;forge.classList.add(kind);window.setTimeout(()=>forge.classList.remove(kind),ms)};
function accept(){pulse('hit-accept',1050)}function reject(){pulse('hit-reject',980)}function block(){pulse('hit-block',1600)}function round(){pulse('hit-round',1100)}
window.addEventListener('fixedcoin:accept',accept);window.addEventListener('fixedcoin:reject',reject);window.addEventListener('fixedcoin:block',block);window.addEventListener('fixedcoin:round',round);
const observer=new MutationObserver(()=>{const a=Number(document.getElementById('acceptedCount')?.textContent)||0;const r=Number(document.getElementById('rejectedCount')?.textContent)||0;if(booted){if(a>lastAccept)accept();if(r>lastReject)reject()}lastAccept=a;lastReject=r;booted=true});
const accepted=document.getElementById('acceptedCount');const rejected=document.getElementById('rejectedCount');if(accepted)observer.observe(accepted,{childList:true,characterData:true,subtree:true});if(rejected)observer.observe(rejected,{childList:true,characterData:true,subtree:true});
})();

(()=>{'use strict';if(window.__FIXEDCOIN_FORGE_OVERHAUL_V1__)return;window.__FIXEDCOIN_FORGE_OVERHAUL_V1__=true;
const stage=document.getElementById('forgeStage');if(!stage)return;const reduce=matchMedia('(prefers-reduced-motion: reduce)');const mobile=()=>matchMedia('(max-width:700px)').matches;const saveData=navigator.connection?.saveData===true;
const cvs=document.createElement('canvas');cvs.className='fo-animation-canvas';cvs.setAttribute('aria-hidden','true');stage.appendChild(cvs);const ctx=cvs.getContext('2d',{alpha:true,desynchronized:true});
let w=0,h=0,dpr=1,raf=0,last=0,visible=true,particles=[],bursts=[],progress=0,targetProgress=0;
const rnd=(a,b)=>a+Math.random()*(b-a),clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
function resize(){const r=stage.getBoundingClientRect();dpr=Math.min(mobile()?1:1.5,devicePixelRatio||1);w=Math.max(1,r.width);h=Math.max(1,r.height);cvs.width=Math.round(w*dpr);cvs.height=Math.round(h*dpr);cvs.style.width=w+'px';cvs.style.height=h+'px';ctx.setTransform(dpr,0,0,dpr,0,0);seed()}
function seed(){particles=[];const n=Math.round((mobile()?42:100)*(saveData?.55:1));for(let i=0;i<n;i++)particles.push({a:rnd(0,Math.PI*2),r:rnd(.16,.39),s:rnd(.12,.42),size:rnd(.7,2.1),alpha:rnd(.18,.72),green:Math.random()>.38})}
function spawn(type){const c={x:w*.5,y:h*.5},n=type==='accept'?18:type==='reject'?13:34;for(let i=0;i<n;i++){const a=rnd(0,Math.PI*2),sp=rnd(45,190);bursts.push({x:c.x,y:c.y,vx:Math.cos(a)*sp,vy:Math.sin(a)*sp,life:0,d:rnd(.42,.9),size:rnd(1,3),type})}}
function draw(now,dt){ctx.clearRect(0,0,w,h);const c={x:w*.5,y:h*.5},t=now*.001;
for(const p of particles){p.a+=dt*p.s;const rr=Math.min(w,h)*p.r,x=c.x+Math.cos(p.a)*rr,y=c.y+Math.sin(p.a)*rr*.56,tw=.45+.55*Math.sin(t*2+p.a*3);ctx.globalAlpha=p.alpha*tw;ctx.fillStyle=p.green?'#59ff91':'#28dfff';ctx.beginPath();ctx.arc(x,y,p.size,0,Math.PI*2);ctx.fill();if(p.size>1.6){ctx.globalAlpha*=.22;ctx.beginPath();ctx.arc(x,y,p.size*5,0,Math.PI*2);ctx.fill()}}
ctx.globalAlpha=.14;ctx.strokeStyle='#3cecff';ctx.lineWidth=1;for(let i=0;i<8;i++){const a=t*.12+i*Math.PI/4,r1=Math.min(w,h)*.18,r2=Math.min(w,h)*.44;ctx.beginPath();ctx.moveTo(c.x+Math.cos(a)*r1,c.y+Math.sin(a)*r1);ctx.lineTo(c.x+Math.cos(a+.018)*r2,c.y+Math.sin(a+.018)*r2);ctx.stroke()}
const p=clamp(progress,0,1);if(p>0){ctx.globalAlpha=.08+.16*p;ctx.strokeStyle='#50ff83';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(c.x,c.y,Math.min(w,h)*(.23+.035*p),-Math.PI/2,-Math.PI/2+Math.PI*2*p);ctx.stroke()}
for(let i=bursts.length-1;i>=0;i--){const b=bursts[i];b.life+=dt;if(b.life>b.d){bursts.splice(i,1);continue}b.x+=b.vx*dt;b.y+=b.vy*dt;b.vx*=.982;b.vy*=.982;const k=1-b.life/b.d;ctx.globalAlpha=k*.9;ctx.fillStyle=b.type==='reject'?'#ff4f5f':b.type==='block'?'#ffe06a':'#55ff8b';ctx.shadowBlur=10;ctx.shadowColor=ctx.fillStyle;ctx.beginPath();ctx.arc(b.x,b.y,b.size*(.7+k),0,Math.PI*2);ctx.fill();ctx.shadowBlur=0}ctx.globalAlpha=1}
function frame(now){if(!visible||reduce.matches){raf=0;return}const dt=Math.min(.033,(now-(last||now-16.7))/1000);last=now;progress+=(targetProgress-progress)*Math.min(1,dt*4);draw(now,dt);raf=requestAnimationFrame(frame)}function wake(){if(!raf&&!reduce.matches){last=performance.now();raf=requestAnimationFrame(frame)}}
function readProgress(){const el=document.getElementById('candidateMeter');if(!el)return;const width=parseFloat(getComputedStyle(el).width)||0,track=el.parentElement?.getBoundingClientRect().width||1;targetProgress=clamp(width/track,0,1)}
new ResizeObserver(resize).observe(stage);new IntersectionObserver(es=>{visible=!!es[0]?.isIntersecting;if(visible)wake();else raf=0}).observe(stage);new MutationObserver(readProgress).observe(document.getElementById('candidateMeter')||stage,{attributes:true,attributeFilter:['style','class','aria-valuenow']});
window.addEventListener('fixedcoin:accept',()=>{spawn('accept');wake()});window.addEventListener('fixedcoin:reject',()=>{spawn('reject');wake()});window.addEventListener('fixedcoin:block',()=>{spawn('block');wake()});window.addEventListener('resize',resize,{passive:true});resize();wake();
})();
