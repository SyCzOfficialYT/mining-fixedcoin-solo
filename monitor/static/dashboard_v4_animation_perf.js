(()=>{"use strict";
if(window.__FIXEDCOIN_ANIMATION_PERF_V3__)return;
window.__FIXEDCOIN_ANIMATION_PERF_V3__=true;

const stage=document.getElementById("forgeStage");
const core=document.getElementById("forgeCore");
const pctEl=document.getElementById("candidatePct");
const track=document.querySelector(".candidate-track");
const accepted=document.getElementById("acceptedCount");
const rejected=document.getElementById("rejectedCount");
if(!stage||!core)return;

const reduce=matchMedia("(prefers-reduced-motion: reduce)");
const saveData=navigator.connection?.saveData===true;
if(reduce.matches)return;

const mobile=()=>innerWidth<=700;
const quality=()=>saveData?0.55:(mobile()?0.72:1);
const dpr=()=>Math.min(mobile()?1:1.5,devicePixelRatio||1);
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
const bezier=(a,c,b,t)=>{const u=1-t;return{x:u*u*a.x+2*u*t*c.x+t*t*b.x,y:u*u*a.y+2*u*t*c.y+t*t*b.y}};

const fx={
 canvas:null,ctx:null,pc:null,pctx:null,
 orbit:[],dust:[],beam:[],events:[],bursts:[],progress:[],
 raf:0,last:0,visible:true,seeded:false,
 geom:{core:{x:0,y:0},accept:{x:0,y:0},reject:{x:0,y:0}},
 progressValue:-1,lastA:Number(accepted?.textContent)||0,lastR:Number(rejected?.textContent)||0,
 lastResize:0
};

function makeCanvas(cls,parent){
 const c=document.createElement("canvas");
 c.className=cls;c.setAttribute("aria-hidden","true");parent.appendChild(c);return c
}
fx.canvas=makeCanvas("fx-animation-canvas",stage);
fx.ctx=fx.canvas.getContext("2d",{alpha:true,desynchronized:true});
if(track){
 fx.pc=makeCanvas("candidate-particle-canvas",track);
 fx.pctx=fx.pc.getContext("2d",{alpha:true,desynchronized:true})
}

function resizeCanvas(c,ctx){
 if(!c||!ctx)return;
 const r=c.getBoundingClientRect(),s=dpr();
 const w=Math.max(1,Math.round(r.width*s)),h=Math.max(1,Math.round(r.height*s));
 if(c.width!==w||c.height!==h){c.width=w;c.height=h}
 ctx.setTransform(s,0,0,s,0,0)
}

function refresh(){
 resizeCanvas(fx.canvas,fx.ctx);resizeCanvas(fx.pc,fx.pctx);
 const sr=stage.getBoundingClientRect(),cr=core.getBoundingClientRect();
 fx.geom.core={x:cr.left+cr.width/2-sr.left,y:cr.top+cr.height/2-sr.top};
 for(const [k,sel] of [["accept",".forge-counter.accepted"],["reject",".forge-counter.rejected"]]){
  const el=stage.querySelector(sel);if(el){const r=el.getBoundingClientRect();
   fx.geom[k]={x:r.left+r.width/2-sr.left,y:r.top+r.height/2-sr.top}
  }
 }
 fx.lastResize=performance.now()
}

function seed(){
 const q=quality(),m=mobile(),base=Math.min(stage.clientWidth,stage.clientHeight);
 const orbitN=Math.round((m?86:190)*q);
 const dustN=Math.round((m?28:70)*q);
 const beamN=Math.round((m?12:28)*q);
 fx.orbit.length=0;fx.dust.length=0;fx.beam.length=0;

 for(let i=0;i<orbitN;i++){
  const a=Math.random()*Math.PI*2,r=base*(.10+Math.random()*.34);
  fx.orbit.push({a,r,sp:(Math.random()<.5?-1:1)*(.00038+Math.random()*.00085),
   e:.62+Math.random()*.32,s:.5+Math.random()*1.65,o:Math.random()*6.28,
   alpha:.12+Math.random()*.38})
 }
 for(let i=0;i<dustN;i++){
  fx.dust.push({x:Math.random()*stage.clientWidth,y:Math.random()*stage.clientHeight,
   vx:(Math.random()-.5)*.025,vy:(Math.random()-.5)*.018,
   s:.45+Math.random()*1.2,a:.05+Math.random()*.18,o:Math.random()*6.28})
 }
 for(let i=0;i<beamN;i++){
  const side=Math.random()<.5?-1:1;
  fx.beam.push({side,t:Math.random(),speed:.018+Math.random()*.04,
   lane:(Math.random()-.5)*24,s:.55+Math.random()*1.2,a:.12+Math.random()*.28})
 }
 fx.seeded=true
}

function seedProgress(p){
 if(!track||!fx.pc)return;
 const end=.06+Math.min(.88,p/100)*.88,n=Math.round((mobile()?10:22)*quality());
 fx.progress.length=0;
 for(let i=0;i<n;i++)fx.progress.push({
  x:end+(Math.random()-.5)*.025,y:.5+(Math.random()-.5)*.28,
  v:.0007+Math.random()*.0018,life:Math.random()*.28,
  max:.45+Math.random()*.55,s:1+Math.random()*2,a:.22+Math.random()*.58,
  phase:Math.random()*6.28
 })
}

function spawnEvent(kind,count){
 const a=fx.geom.core,b=kind==="accept"?fx.geom.accept:fx.geom.reject;
 const dx=b.x-a.x,dy=b.y-a.y,dist=Math.hypot(dx,dy)||1,nx=-dy/dist,ny=dx/dist;
 const n=Math.min(mobile()?4:7,count||6);
 for(let i=0;i<n;i++){
  const bend=(kind==="accept"?-55:55)+(Math.random()-.5)*24;
  const control={x:(a.x+b.x)/2+nx*bend,y:(a.y+b.y)/2+ny*bend};
  fx.events.push({kind,t:-i*.055,d:.72+Math.random()*.20,a,b,c:control,nx,ny,
   spread:(Math.random()-.5)*(mobile()?42:76),size:1.1+Math.random()*1.7})
 }
 spawnBurst(kind,b);
 if(fx.events.length>96)fx.events.splice(0,fx.events.length-96)
}

function spawnBurst(kind,pos){
 const n=Math.round((mobile()?8:18)*quality());
 for(let i=0;i<n;i++){
  const a=Math.random()*Math.PI*2,s=.018+Math.random()*.045;
  fx.bursts.push({kind,x:pos.x,y:pos.y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,
   life:0,max:.28+Math.random()*.38,size:.8+Math.random()*1.7,a:.28+Math.random()*.45})
 }
 if(fx.bursts.length>72)fx.bursts.splice(0,fx.bursts.length-72)
}

function syncProgress(){
 if(!track||!fx.pc)return;
 const p=clamp(parseFloat(String(pctEl?.textContent||"0").replace("%",""))||0,0,100);
 if(fx.progressValue<0){fx.progressValue=p;seedProgress(p);return}
 if(Math.abs(p-fx.progressValue)>.01){
  const delta=p-fx.progressValue,n=Math.min(18,Math.max(2,Math.round(Math.abs(delta)*.75)));
  const end=.06+Math.min(.88,p/100)*.88;
  for(let i=0;i<n;i++)fx.progress.push({
   x:end+(Math.random()-.5)*.035,y:.5+(Math.random()-.5)*.32,
   v:.0015+Math.random()*.0028,life:0,max:.35+Math.random()*.5,
   s:1+Math.random()*2,a:.25+Math.random()*.55,phase:Math.random()*6.28
  });
  fx.progressValue=p
 }
}

function drawParticle(ctx,x,y,s,a){
 ctx.globalAlpha=a;ctx.fillRect(x-s/2,y-s/2,s,s);
 if(s>1.8){ctx.globalAlpha=a*.16;ctx.fillRect(x-s*1.1,y-s*1.1,s*2.2,s*2.2)}
}

function renderForge(dt,now){
 const ctx=fx.ctx,w=fx.canvas.clientWidth,h=fx.canvas.clientHeight;
 if(!ctx)return;
 ctx.clearRect(0,0,w,h);ctx.globalCompositeOperation="lighter";
 const c=fx.geom.core,t=now*.001;

 // 1) Slow ambient dust.
 for(const p of fx.dust){
  p.x+=p.vx*dt*60;p.y+=p.vy*dt*60;
  if(p.x<0)p.x=w;if(p.x>w)p.x=0;if(p.y<0)p.y=h;if(p.y>h)p.y=0;
  drawParticle(ctx,p.x,p.y,p.s,p.a*(.7+.3*Math.sin(t*.7+p.o)))
 }

 // 2) Dense orbital FIXCORE field.
 for(const p of fx.orbit){
  p.a+=p.sp*dt*16.67;
  const breathe=1+Math.sin(t+p.o)*.035;
  const x=c.x+Math.cos(p.a)*p.r*breathe;
  const y=c.y+Math.sin(p.a)*p.r*p.e*breathe;
  drawParticle(ctx,x,y,p.s,p.alpha*(.84+.16*Math.sin(t*1.5+p.o)))
 }

 // 3) Directional core beam particles.
 for(const p of fx.beam){
  p.t=(p.t+p.speed*dt)%1;
  const x=p.side<0?c.x-228+p.t*166:c.x+62+p.t*166;
  const y=c.y+p.lane*(.55+.45*Math.sin(t+p.t*8));
  drawParticle(ctx,x,y,p.s,p.a*(1-p.t))
 }

 // 4) Accept/reject event trails.
 for(let i=fx.events.length-1;i>=0;i--){
  const e=fx.events[i];e.t+=dt;
  if(e.t<0)continue;
  const q=e.t/e.d;
  if(q>=1){fx.events.splice(i,1);continue}
  const p=bezier(e.a,e.c,e.b,q),spread=Math.sin(Math.PI*q)*e.spread;
  const x=p.x+e.nx*spread,y=p.y+e.ny*spread;
  const fade=q<.08?q/.08:q>.82?(1-q)/.18:1;
  ctx.fillStyle=e.kind==="accept"?"#62ff82":"#ff6b6b";
  drawParticle(ctx,x,y,e.size*(1+.5*q),.78*fade)
 }

 // 5) Impact burst at share counter.
 for(let i=fx.bursts.length-1;i>=0;i--){
  const b=fx.bursts[i];b.life+=dt;
  if(b.life>b.max){fx.bursts.splice(i,1);continue}
  b.x+=b.vx*dt*60;b.y+=b.vy*dt*60;
  const fade=1-b.life/b.max;
  ctx.fillStyle=b.kind==="accept"?"#7aff96":"#ff6565";
  drawParticle(ctx,b.x,b.y,b.size,fade*b.a)
 }
 ctx.globalCompositeOperation="source-over"
}

function renderProgress(dt,now){
 if(!fx.pctx||!fx.pc)return;
 const ctx=fx.pctx,w=fx.pc.clientWidth,h=fx.pc.clientHeight;
 ctx.clearRect(0,0,w,h);ctx.globalCompositeOperation="lighter";
 for(let i=fx.progress.length-1;i>=0;i--){
  const p=fx.progress[i];p.life+=dt;p.x+=p.v*dt*60;
  p.y+=Math.sin(now*.002+p.phase)*.00012;
  if(p.life>p.max||p.x>1.03){fx.progress.splice(i,1);continue}
  const fade=Math.min(1,p.life/.06,(p.max-p.life)/.12);
  ctx.fillStyle="#63ff80";drawParticle(ctx,p.x*w,p.y*h,p.s,fade*p.a)
 }
 ctx.globalCompositeOperation="source-over"
}

function frame(now){
 if(!fx.visible){fx.raf=0;return}
 const dt=Math.min(.033,(now-fx.last||16.67)/1000);fx.last=now;
 syncProgress();renderForge(dt,now);renderProgress(dt,now);
 fx.raf=requestAnimationFrame(frame)
}
function wake(){if(!fx.raf){fx.last=performance.now();fx.raf=requestAnimationFrame(frame)}}

new IntersectionObserver(es=>{
 fx.visible=es.some(e=>e.isIntersecting);
 if(fx.visible){refresh();wake()}
},{threshold:0.01}).observe(stage);

const ro=new ResizeObserver(()=>{
 const now=performance.now();
 if(now-fx.lastResize<120)return;
 refresh();seed()
});
ro.observe(stage);if(track)ro.observe(track);

addEventListener("resize",()=>{
 const now=performance.now();
 if(now-fx.lastResize<120)return;
 refresh();seed()
},{passive:true});

const countObs=new MutationObserver(()=>{
 const a=Number(accepted?.textContent)||0,r=Number(rejected?.textContent)||0;
 if(a>fx.lastA)spawnEvent("accept",Math.min(3,a-fx.lastA));
 if(r>fx.lastR)spawnEvent("reject",Math.min(3,r-fx.lastR));
 fx.lastA=a;fx.lastR=r
});
if(accepted)countObs.observe(accepted,{childList:true,characterData:true,subtree:true});
if(rejected)countObs.observe(rejected,{childList:true,characterData:true,subtree:true});
addEventListener("fixedcoin:accept",()=>spawnEvent("accept",1),{passive:true});
addEventListener("fixedcoin:reject",()=>spawnEvent("reject",1),{passive:true});

seed();refresh();syncProgress();wake()
})();
