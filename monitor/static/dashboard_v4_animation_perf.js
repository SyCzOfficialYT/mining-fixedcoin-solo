(()=>{
'use strict';
if(window.__FIXEDCOIN_ANIMATION_PERF_V2__)return;
window.__FIXEDCOIN_ANIMATION_PERF_V2__=true;
const stage=document.getElementById('forgeStage');
const core=document.getElementById('forgeCore');
const pctEl=document.getElementById('candidatePct');
const track=document.querySelector('.candidate-track');
const accepted=document.getElementById('acceptedCount');
const rejected=document.getElementById('rejectedCount');
if(!stage||!core)return;
const reduce=matchMedia('(prefers-reduced-motion: reduce)');
if(reduce.matches)return;
const mobile=()=>innerWidth<=700;
const dpr=()=>Math.min(mobile()?1:1.5,devicePixelRatio||1);
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
const bezier=(a,c,b,t)=>{const u=1-t;return{x:u*u*a.x+2*u*t*c.x+t*t*b.x,y:u*u*a.y+2*u*t*c.y+t*t*b.y}};
const fx={canvas:null,ctx:null,pc:null,pctx:null,particles:[],events:[],progress:[],raf:0,last:0,visible:true,geom:{core:{x:0,y:0},accept:{x:0,y:0},reject:{x:0,y:0}},progressValue:-1,lastA:Number(accepted?.textContent)||0,lastR:Number(rejected?.textContent)||0};
function makeCanvas(cls,parent){const c=document.createElement('canvas');c.className=cls;c.setAttribute('aria-hidden','true');parent.appendChild(c);return c}
fx.canvas=makeCanvas('fx-animation-canvas',stage);fx.ctx=fx.canvas.getContext('2d',{alpha:true,desynchronized:true});
if(track){fx.pc=makeCanvas('candidate-particle-canvas',track);fx.pctx=fx.pc.getContext('2d',{alpha:true,desynchronized:true})}
function resizeCanvas(c,ctx){if(!c||!ctx)return;const r=c.getBoundingClientRect(),s=dpr();c.width=Math.max(1,Math.round(r.width*s));c.height=Math.max(1,Math.round(r.height*s));ctx.setTransform(s,0,0,s,0,0)}
function refresh(){resizeCanvas(fx.canvas,fx.ctx);resizeCanvas(fx.pc,fx.pctx);const sr=stage.getBoundingClientRect(),cr=core.getBoundingClientRect();fx.geom.core={x:cr.left+cr.width/2-sr.left,y:cr.top+cr.height/2-sr.top};for(const [k,sel] of [['accept','.forge-counter.accepted'],['reject','.forge-counter.rejected']]){const el=stage.querySelector(sel);if(el){const r=el.getBoundingClientRect();fx.geom[k]={x:r.left+r.width/2-sr.left,y:r.top+r.height/2-sr.top}}}}
function seed(){const count=mobile()?75:150;fx.particles.length=0;const base=Math.min(stage.clientWidth,stage.clientHeight);for(let i=0;i<count;i++){const a=Math.random()*Math.PI*2,r=base*(.12+Math.random()*.31);fx.particles.push({a,r,sp:(Math.random()-.5)*.00035+(Math.random()<.5?-1:1)*(.00045+Math.random()*.00055),e:.68+Math.random()*.28,s:.55+Math.random()*1.65,o:Math.random()*6.28,alpha:.14+Math.random()*.42})}}
function seedProgress(p){if(!track||!fx.pc)return;const end=0.06+Math.min(.88,p/100)*.88;const n=mobile()?8:18;fx.progress.length=0;for(let i=0;i<n;i++)fx.progress.push({x:end+(Math.random()-.5)*.025,y:.5+(Math.random()-.5)*.28,v:.0007+Math.random()*.0018,life:Math.random()*.28,max:.45+Math.random()*.55,s:1+Math.random()*2,a:.22+Math.random()*.58})}
function spawnEvent(kind,count){const a=fx.geom.core,b=kind==='accept'?fx.geom.accept:fx.geom.reject;const dx=b.x-a.x,dy=b.y-a.y,dist=Math.hypot(dx,dy)||1,nx=-dy/dist,ny=dx/dist;const n=Math.min(mobile()?4:6,count||6);for(let i=0;i<n;i++){const bend=(kind==='accept'?-55:55)+(Math.random()-.5)*24,control={x:(a.x+b.x)/2+nx*bend,y:(a.y+b.y)/2+ny*bend};fx.events.push({kind,t:-i*.07,d:.9+Math.random()*.18,a,b,c:control,nx,ny,spread:(Math.random()-.5)*(mobile()?48:76),size:1.1+Math.random()*1.7});if(fx.events.length>80)fx.events.splice(0,fx.events.length-80)}}
function syncProgress(){if(!track||!fx.pc)return;const p=clamp(parseFloat(String(pctEl?.textContent||'0').replace('%',''))||0,0,100);if(fx.progressValue<0){fx.progressValue=p;seedProgress(p);return}if(Math.abs(p-fx.progressValue)>.01){const delta=p-fx.progressValue;const n=Math.min(14,Math.max(2,Math.round(Math.abs(delta)*.7)));const end=0.06+Math.min(.88,p/100)*.88;for(let i=0;i<n;i++)fx.progress.push({x:end+(Math.random()-.5)*.035,y:.5+(Math.random()-.5)*.32,v:.0015+Math.random()*.0028,life:0,max:.35+Math.random()*.5,s:1+Math.random()*2,a:.25+Math.random()*.55});fx.progressValue=p}}
function drawParticle(ctx,x,y,s,a){ctx.globalAlpha=a;ctx.fillRect(x-s/2,y-s/2,s,s);if(s>1.8){ctx.globalAlpha=a*.18;ctx.fillRect(x-s*1.2,y-s*1.2,s*2.4,s*2.4)}}
function renderForge(dt,now){const ctx=fx.ctx,w=fx.canvas.clientWidth,h=fx.canvas.clientHeight;if(!ctx)return;ctx.clearRect(0,0,w,h);ctx.globalCompositeOperation='lighter';const c=fx.geom.core;for(const p of fx.particles){p.a+=p.sp*dt*16.67;const breathe=1+Math.sin(now*.001+p.o)*.035;const x=c.x+Math.cos(p.a)*p.r*breathe;const y=c.y+Math.sin(p.a)*p.r*p.e*breathe;ctx.fillStyle='#59ff78';drawParticle(ctx,x,y,p.s,p.alpha*(.85+.15*Math.sin(now*.0015+p.o)))}
for(let i=fx.events.length-1;i>=0;i--){const e=fx.events[i];e.t+=dt;if(e.t<0)continue;const t=e.t/e.d;if(t>=1){fx.events.splice(i,1);continue}const p=bezier(e.a,e.c,e.b,t),spread=Math.sin(Math.PI*t)*e.spread,x=p.x+e.nx*spread,y=p.y+e.ny*spread,fade=t<.08?t/.08:t>.82?(1-t)/.18:1;ctx.fillStyle=e.kind==='accept'?'#62ff82':'#ff6b6b';drawParticle(ctx,x,y,e.size*(1+.5*t),.78*fade);if(t>.9){ctx.globalAlpha=.22*fade;ctx.fillRect(e.b.x-7,e.b.y-7,14,14)}}ctx.globalCompositeOperation='source-over'}
function renderProgress(dt){if(!fx.pctx||!fx.pc)return;const ctx=fx.pctx,w=fx.pc.clientWidth,h=fx.pc.clientHeight;ctx.clearRect(0,0,w,h);ctx.globalCompositeOperation='lighter';for(let i=fx.progress.length-1;i>=0;i--){const p=fx.progress[i];p.life+=dt;p.x+=p.v*dt*60;p.y+=(Math.random()-.5)*.002;if(p.life>p.max||p.x>1.03){fx.progress.splice(i,1);continue}const fade=Math.min(1,p.life/.06,(p.max-p.life)/.12);ctx.fillStyle='#63ff80';drawParticle(ctx,p.x*w,p.y*h,p.s,fade*p.a)}ctx.globalCompositeOperation='source-over'}
function frame(now){if(!fx.visible){fx.raf=0;return}const dt=Math.min(.033,(now-fx.last||16.67)/1000);fx.last=now;syncProgress();renderForge(dt,now);renderProgress(dt);fx.raf=requestAnimationFrame(frame)}
function wake(){if(!fx.raf){fx.last=performance.now();fx.raf=requestAnimationFrame(frame)}}
new IntersectionObserver(es=>{fx.visible=es.some(e=>e.isIntersecting);if(fx.visible){refresh();wake()}},{threshold:0.01}).observe(stage);
const ro=new ResizeObserver(()=>{refresh();seed()});ro.observe(stage);if(track)ro.observe(track);addEventListener('resize',()=>{refresh();seed()},{passive:true});
const countObs=new MutationObserver(()=>{const a=Number(accepted?.textContent)||0,r=Number(rejected?.textContent)||0;if(a>fx.lastA)spawnEvent('accept',Math.min(3,a-fx.lastA));if(r>fx.lastR)spawnEvent('reject',Math.min(3,r-fx.lastR));fx.lastA=a;fx.lastR=r});
if(accepted)countObs.observe(accepted,{childList:true,characterData:true,subtree:true});if(rejected)countObs.observe(rejected,{childList:true,characterData:true,subtree:true});
addEventListener('fixedcoin:accept',()=>spawnEvent('accept',1),{passive:true});addEventListener('fixedcoin:reject',()=>spawnEvent('reject',1),{passive:true});
seed();refresh();syncProgress();wake();
})();
