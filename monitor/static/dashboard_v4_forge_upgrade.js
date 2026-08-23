(()=>{
'use strict';
if(window.__FIXEDCOIN_FORGE_UPGRADE__) return;
window.__FIXEDCOIN_FORGE_UPGRADE__=true;

const stage=document.getElementById('forgeStage');
const core=document.getElementById('forgeCore');
const candidate=document.getElementById('candidate');
const track=document.querySelector('.candidate-track');
const pctEl=document.getElementById('candidatePct');
if(!stage||!core||!candidate||!track||!pctEl) return;

// Central FIXCORE progress field. It is deliberately independent from the
// existing share-impact canvas so share particles and progress particles can
// coexist without clearing each other.
const coreCanvas=document.createElement('canvas');
coreCanvas.className='progress-particle-canvas';
coreCanvas.setAttribute('aria-hidden','true');
stage.appendChild(coreCanvas);
const cctx=coreCanvas.getContext('2d',{alpha:true});
let coreParticles=[],progressUnits=-1,coreSpawnQueue=0,lastTs=performance.now();

function resizeCanvas(canvas,ctx){
  const r=canvas.getBoundingClientRect(),d=Math.min(2,window.devicePixelRatio||1);
  canvas.width=Math.max(1,Math.round(r.width*d));
  canvas.height=Math.max(1,Math.round(r.height*d));
  ctx.setTransform(d,0,0,d,0,0);
}
function corePoint(){
  const cr=core.getBoundingClientRect(),sr=coreCanvas.getBoundingClientRect();
  return {x:cr.left+cr.width/2-sr.left,y:cr.top+cr.height*.43-sr.top};
}
function spawnCoreParticle(){
  const cp=corePoint(),a=Math.random()*Math.PI*2;
  const radius=Math.min(coreCanvas.clientWidth,coreCanvas.clientHeight)*(.19+Math.random()*.25);
  coreParticles.push({
    x:cp.x+Math.cos(a)*radius,
    y:cp.y+Math.sin(a)*radius*.72,
    angle:a,radius,life:0,max:9000+Math.random()*9000,
    size:.55+Math.random()*1.8,alpha:.18+Math.random()*.55,
    speed:.006+Math.random()*.010,
    orbit:(Math.random()<.5?-1:1)*(.00025+Math.random()*.00065),phase:Math.random()*Math.PI*2
  });
  if(coreParticles.length>1500) coreParticles.splice(0,coreParticles.length-1500);
}
function seedCoreParticles(progress){
  const target=Math.min(1500,Math.round(progress*5));
  while(coreParticles.length<target) spawnCoreParticle();
}
function drawCoreParticles(dt,now){
  const w=coreCanvas.clientWidth,h=coreCanvas.clientHeight;
  cctx.clearRect(0,0,w,h);
  const cp=corePoint();
  for(let i=coreParticles.length-1;i>=0;i--){
    const p=coreParticles[i];p.life+=dt;p.angle+=p.orbit*dt;p.radius*=Math.pow(.99992,dt);
    const tx=cp.x+Math.cos(p.angle)*p.radius,ty=cp.y+Math.sin(p.angle)*p.radius*.72;
    p.x+=(tx-p.x)*p.speed*dt;p.y+=(ty-p.y)*p.speed*dt;
    const fade=Math.min(1,p.life/1200)*Math.min(1,(p.max-p.life)/1800);
    if(fade<=0){coreParticles.splice(i,1);continue}
    const pulse=.72+.28*Math.sin(now*.003+p.phase);
    cctx.beginPath();cctx.arc(p.x,p.y,p.size,0,Math.PI*2);
    cctx.fillStyle=`rgba(92,255,122,${fade*p.alpha*pulse})`;
    cctx.shadowBlur=8;cctx.shadowColor='rgba(70,255,110,.75)';cctx.fill();
  }
  cctx.shadowBlur=0;
}

// Candidate progress conduit. Every observed 0.001% increase queues one
// particle; the queue is drained gradually to create a continuous liquid flow.
const trackCanvas=document.createElement('canvas');
trackCanvas.className='candidate-particle-canvas';
trackCanvas.setAttribute('aria-hidden','true');
track.appendChild(trackCanvas);
const tctx=trackCanvas.getContext('2d',{alpha:true});
let tParticles=[];
function resizeTrackCanvas(){
  const r=trackCanvas.getBoundingClientRect(),d=Math.min(2,window.devicePixelRatio||1);
  trackCanvas.width=Math.max(1,Math.round(r.width*d));trackCanvas.height=Math.max(1,Math.round(r.height*d));tctx.setTransform(d,0,0,d,0,0);
}
function spawnTrackParticle(progress){
  const w=trackCanvas.clientWidth,h=trackCanvas.clientHeight,x=Math.max(1,Math.min(w-1,w*(progress/100)));
  tParticles.push({x:x+(Math.random()-.5)*5,y:h*.5+(Math.random()-.5)*3,vx:8+Math.random()*24,vy:(Math.random()-.5)*13,life:0,max:650+Math.random()*900,size:.5+Math.random()*1.7,alpha:.25+Math.random()*.6});
  if(tParticles.length>900)tParticles.shift();
}
function drawTrackParticles(dt){
  const w=trackCanvas.clientWidth,h=trackCanvas.clientHeight;tctx.clearRect(0,0,w,h);
  for(let i=tParticles.length-1;i>=0;i--){
    const p=tParticles[i];p.life+=dt;p.x+=p.vx*dt/1000;p.y+=p.vy*dt/1000;p.vy*=.995;
    const a=Math.sin(Math.min(1,p.life/p.max)*Math.PI)*p.alpha;
    if(p.life>=p.max||p.x>w+8){tParticles.splice(i,1);continue}
    tctx.beginPath();tctx.arc(p.x,p.y,p.size,0,Math.PI*2);tctx.fillStyle=`rgba(93,255,119,${a})`;tctx.shadowBlur=8;tctx.shadowColor='rgba(70,255,110,.8)';tctx.fill();
  }
  tctx.shadowBlur=0;
}
function readProgress(){
  const n=parseFloat(String(pctEl.textContent||'0').replace('%',''));
  return Number.isFinite(n)?Math.max(0,Math.min(100,n)):0;
}
function progressChanged(){
  const p=readProgress(),units=Math.round(p*1000);
  if(progressUnits<0){progressUnits=units;seedCoreParticles(p);return}
  const delta=units-progressUnits;
  if(delta>0){coreSpawnQueue=Math.min(3000,coreSpawnQueue+delta);progressUnits=units}
  else if(delta<0)progressUnits=units;
}
function tick(now){
  const dt=Math.min(50,now-lastTs);lastTs=now;progressChanged();
  const spawn=Math.min(18,coreSpawnQueue);
  for(let i=0;i<spawn;i++){spawnCoreParticle();spawnTrackParticle(readProgress())}
  coreSpawnQueue-=spawn;drawCoreParticles(dt,now);drawTrackParticles(dt);requestAnimationFrame(tick);
}

const obs=new MutationObserver(progressChanged);
obs.observe(pctEl,{characterData:true,childList:true,subtree:true});
function resizeAll(){resizeCanvas(coreCanvas,cctx);resizeTrackCanvas()}
window.addEventListener('resize',resizeAll,{passive:true});
resizeAll();progressChanged();requestAnimationFrame(tick);

// Strong, synchronized block-found choreography for both the central core and
// the network-proximity instrument. The existing realtime client remains the
// only source of truth; this merely reacts to its established state classes.
const forge=document.getElementById('forge');
let blockTimer=0;
function blockFound(){
  stage.classList.remove('progress-forged');candidate.classList.remove('block-found');
  void stage.offsetWidth;stage.classList.add('progress-forged');candidate.classList.add('block-found');
  coreSpawnQueue=Math.min(900,coreSpawnQueue+240);
  clearTimeout(blockTimer);
  blockTimer=setTimeout(()=>{stage.classList.remove('progress-forged');candidate.classList.remove('block-found')},3600);
}
const classObs=new MutationObserver(muts=>{
  for(const m of muts){
    if(m.type!=='attributes'||m.attributeName!=='class')continue;
    const cls=String(stage.className)+' '+String(candidate.className)+' '+String(forge?.className||'');
    if(/hit-block|explode|block-found/.test(cls)){blockFound();break}
  }
});
classObs.observe(stage,{attributes:true,attributeFilter:['class']});
classObs.observe(candidate,{attributes:true,attributeFilter:['class']});
if(forge)classObs.observe(forge,{attributes:true,attributeFilter:['class']});
})();
