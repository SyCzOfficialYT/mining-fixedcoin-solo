(()=>{
'use strict';
if(window.__FIXEDCOIN_FORGE_UPGRADE__) return;
window.__FIXEDCOIN_FORGE_UPGRADE__=true;

const stage=document.getElementById('forgeStage');
const core=document.getElementById('forgeCore');
const candidate=document.getElementById('candidate');
const track=document.querySelector('.candidate-track');
const pctEl=document.getElementById('candidatePct');
const candidateMeter=document.getElementById('candidateMeter');
if(!stage||!core||!candidate||!track||!pctEl) return;

const dpr=()=>Math.min(2,window.devicePixelRatio||1);
const clamp=(n,a=0,b=100)=>Math.max(a,Math.min(b,Number(n)||0));

/* -------------------------------------------------------------------------- */
/* FIXCORE PROGRESS FIELD                                                     */
/*                                                                            */
/* One observed +0.001% progress step = one new persistent particle.          */
/* The particles live long enough to form the same dense, liquid energy field */
/* visible in the reference instead of appearing as short random dust bursts. */
/* -------------------------------------------------------------------------- */
const coreCanvas=document.createElement('canvas');
coreCanvas.className='progress-particle-canvas';
coreCanvas.setAttribute('aria-hidden','true');
stage.appendChild(coreCanvas);
const cctx=coreCanvas.getContext('2d',{alpha:true});
let coreParticles=[];
let progressUnits=-1;
let progressQueue=0;
let progressPulseUntil=0;
let lastTs=performance.now();

function resizeCanvas(canvas,ctx){
  const r=canvas.getBoundingClientRect(),scale=dpr();
  canvas.width=Math.max(1,Math.round(r.width*scale));
  canvas.height=Math.max(1,Math.round(r.height*scale));
  ctx.setTransform(scale,0,0,scale,0,0);
}
function corePoint(){
  const cr=core.getBoundingClientRect(),sr=coreCanvas.getBoundingClientRect();
  return {x:cr.left+cr.width/2-sr.left,y:cr.top+cr.height/2-sr.top};
}
function spawnCoreParticle(flash=false){
  const cp=corePoint();
  const a=Math.random()*Math.PI*2;
  const base=Math.min(coreCanvas.clientWidth,coreCanvas.clientHeight);
  const radius=base*(flash?.12:(.17+Math.random()*.26));
  coreParticles.push({
    x:cp.x+Math.cos(a)*radius,
    y:cp.y+Math.sin(a)*radius*(.72+Math.random()*.28),
    angle:a,
    radius,
    life:0,
    max:15000+Math.random()*22000,
    size:.7+Math.random()*2.2,
    alpha:.2+Math.random()*.62,
    orbit:(Math.random()<.5?-1:1)*(.00022+Math.random()*.00055),
    inward:.00045+Math.random()*.0007,
    phase:Math.random()*Math.PI*2,
    flash:flash?1:0
  });
  if(coreParticles.length>1800) coreParticles.splice(0,coreParticles.length-1800);
}
function seedCoreParticles(progress){
  const target=Math.min(1800,Math.round(progress*1000));
  while(coreParticles.length<target) spawnCoreParticle(false);
}
function renderCoreParticles(dt,now){
  const w=coreCanvas.clientWidth,h=coreCanvas.clientHeight;
  cctx.clearRect(0,0,w,h);
  const cp=corePoint();
  const pulse=now<progressPulseUntil;
  for(let i=coreParticles.length-1;i>=0;i--){
    const p=coreParticles[i];
    p.life+=dt;
    p.angle+=p.orbit*dt;
    const lifeFade=Math.min(1,p.life/900)*Math.min(1,(p.max-p.life)/3200);
    if(lifeFade<=0){coreParticles.splice(i,1);continue}
    p.radius=Math.max(20,p.radius*(1-p.inward*dt*.001));
    const wobble=1+Math.sin(now*.0015+p.phase)*.025;
    const x=cp.x+Math.cos(p.angle)*p.radius*wobble;
    const y=cp.y+Math.sin(p.angle)*p.radius*(.72+Math.sin(now*.001+p.phase)*.035);
    p.x+=(x-p.x)*.06;p.y+=(y-p.y)*.06;
    const glow=pulse?.24:.0;
    const a=Math.min(1,lifeFade)*(p.alpha+glow)*(p.flash?1.25:1);
    cctx.beginPath();
    cctx.arc(p.x,p.y,p.size+(pulse?.4:0),0,Math.PI*2);
    cctx.fillStyle=`rgba(95,255,125,${a})`;
    cctx.shadowBlur=7+(pulse?11:0);
    cctx.shadowColor=p.flash?'rgba(200,255,210,.95)':'rgba(70,255,110,.85)';
    cctx.fill();
  }
  cctx.shadowBlur=0;
}

/* -------------------------------------------------------------------------- */
/* CANDIDATE PROGRESS PARTICLES                                               */
/*                                                                            */
/* Every +0.001% adds exactly one persistent energy particle.                  */
/* They accumulate inside the filled section, creating a smooth liquid stream */
/* instead of particles appearing only at the current endpoint.              */
/* -------------------------------------------------------------------------- */
const trackCanvas=document.createElement('canvas');
trackCanvas.className='candidate-particle-canvas';
trackCanvas.setAttribute('aria-hidden','true');
track.appendChild(trackCanvas);
const tctx=trackCanvas.getContext('2d',{alpha:true});
let trackParticles=[];

function resizeTrackCanvas(){
  const r=trackCanvas.getBoundingClientRect(),scale=dpr();
  trackCanvas.width=Math.max(1,Math.round(r.width*scale));
  trackCanvas.height=Math.max(1,Math.round(r.height*scale));
  tctx.setTransform(scale,0,0,scale,0,0);
}
function spawnTrackParticle(progress,flash=false){
  const w=trackCanvas.clientWidth,h=trackCanvas.clientHeight;
  const fill=Math.max(2,Math.min(w-2,w*progress/100));
  const x=2+Math.random()*Math.max(2,fill-2);
  trackParticles.push({
    x,
    y:h*.52+(Math.random()-.5)*5,
    vx:18+Math.random()*30,
    vy:(Math.random()-.5)*18,
    life:0,
    max:5000+Math.random()*11000,
    size:.7+Math.random()*2.3,
    alpha:.18+Math.random()*.68,
    phase:Math.random()*6.28,
    flash:flash?1:0
  });
  if(trackParticles.length>1400) trackParticles.splice(0,trackParticles.length-1400);
}
function renderTrackParticles(dt,now){
  const w=trackCanvas.clientWidth,h=trackCanvas.clientHeight;
  tctx.clearRect(0,0,w,h);
  const pulse=now<progressPulseUntil;
  for(let i=trackParticles.length-1;i>=0;i--){
    const p=trackParticles[i];p.life+=dt;
    p.x+=p.vx*dt/1000;p.y+=p.vy*dt/1000;p.vy*=.998;
    const fade=Math.min(1,p.life/450)*Math.min(1,(p.max-p.life)/1800);
    if(fade<=0||p.x>w+10){trackParticles.splice(i,1);continue}
    const a=fade*(p.alpha+(pulse?.16:0))*(p.flash?1.2:1);
    const s=p.size+(pulse?.35:0);
    tctx.beginPath();tctx.arc(p.x,p.y,s,0,Math.PI*2);
    tctx.fillStyle=`rgba(101,255,126,${a})`;
    tctx.shadowBlur=7+(pulse?8:0);tctx.shadowColor='rgba(72,255,110,.9)';tctx.fill();
  }
  tctx.shadowBlur=0;
}

function readProgress(){
  const n=parseFloat(String(pctEl.textContent||'0').replace('%',''));
  return Number.isFinite(n)?clamp(n):0;
}
function currentUnits(){return Math.round(readProgress()*1000)}
function triggerProgressPulse(){
  progressPulseUntil=performance.now()+260;
  stage.classList.remove('progress-step');
  candidate.classList.remove('progress-step');
  void stage.offsetWidth;
  stage.classList.add('progress-step');
  candidate.classList.add('progress-step');
  window.setTimeout(()=>{stage.classList.remove('progress-step');candidate.classList.remove('progress-step')},280);
}
function queueProgressParticles(delta,progress){
  const count=Math.min(delta,4000);
  progressQueue=Math.min(4000,progressQueue+count);
  // For a real step, visibly place the first particle immediately at the
  // current progress so the UI never waits for the animation queue.
  spawnCoreParticle(true);
  spawnTrackParticle(progress,true);
  triggerProgressPulse();
}
function syncProgress(){
  const progress=readProgress();
  const units=currentUnits();
  if(progressUnits<0){progressUnits=units;seedCoreParticles(progress);return}
  const delta=units-progressUnits;
  if(delta>0){queueProgressParticles(delta,progress);progressUnits=units}
  else if(delta<0){progressUnits=units}
}
function drainProgressQueue(){
  const progress=readProgress();
  const n=Math.min(24,progressQueue);
  for(let i=0;i<n;i++){
    spawnCoreParticle(false);
    spawnTrackParticle(progress,false);
  }
  progressQueue-=n;
}

function tick(now){
  const dt=Math.min(48,now-lastTs);lastTs=now;
  syncProgress();
  drainProgressQueue();
  renderCoreParticles(dt,now);
  renderTrackParticles(dt,now);
  requestAnimationFrame(tick);
}

const progressObserver=new MutationObserver(syncProgress);
progressObserver.observe(pctEl,{characterData:true,childList:true,subtree:true});
window.addEventListener('resize',()=>{resizeCanvas(coreCanvas,cctx);resizeTrackCanvas()},{passive:true});
resizeCanvas(coreCanvas,cctx);resizeTrackCanvas();
syncProgress();
requestAnimationFrame(tick);

/* -------------------------------------------------------------------------- */
/* BLOCK FOUND                                                                */
/* -------------------------------------------------------------------------- */
const forge=document.getElementById('forge');
let blockTimer=0;
function blockFound(){
  stage.classList.remove('progress-forged');candidate.classList.remove('block-found');
  void stage.offsetWidth;
  stage.classList.add('progress-forged');
  candidate.classList.add('block-found');
  progressQueue=Math.min(1200,progressQueue+240);
  for(let i=0;i<40;i++){spawnCoreParticle(true);spawnTrackParticle(100,true)}
  clearTimeout(blockTimer);
  blockTimer=setTimeout(()=>{stage.classList.remove('progress-forged');candidate.classList.remove('block-found')},3600);
}
const classObserver=new MutationObserver(muts=>{
  for(const m of muts){
    if(m.type!=='attributes'||m.attributeName!=='class')continue;
    const cls=String(stage.className)+' '+String(candidate.className)+' '+String(forge?.className||'');
    if(/hit-block|explode|block-found/.test(cls)){blockFound();break}
  }
});
classObserver.observe(stage,{attributes:true,attributeFilter:['class']});
classObserver.observe(candidate,{attributes:true,attributeFilter:['class']});
if(forge)classObserver.observe(forge,{attributes:true,attributeFilter:['class']});
})();
