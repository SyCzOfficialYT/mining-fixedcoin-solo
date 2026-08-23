(()=>{
'use strict';
if(window.__FIXEDCOIN_FORGE_UPGRADE__) return;
window.__FIXEDCOIN_FORGE_UPGRADE__=true;

const stage=document.getElementById('forgeStage');
const core=document.getElementById('forgeCore');
const candidate=document.getElementById('candidate');
const pctEl=document.getElementById('candidatePct');
if(!stage||!core||!candidate||!pctEl) return;

const dpr=()=>Math.min(2,window.devicePixelRatio||1);
const clamp=(n,a=0,b=100)=>Math.max(a,Math.min(b,Number(n)||0));

/* ------------------------------------------------------------------------- */
/* FIXCORE PROGRESS FIELD                                                    */
/*                                                                           */
/* Every +0.001% adds one persistent particle. Particles NEVER travel to     */
/* the share cards and do not disappear while progress is rising. The field */
/* remains physically centered around FIXCORE and simply becomes denser.     */
/* ------------------------------------------------------------------------- */
const canvas=document.createElement('canvas');
canvas.className='progress-particle-canvas';
canvas.setAttribute('aria-hidden','true');
stage.appendChild(canvas);
const ctx=canvas.getContext('2d',{alpha:true});
let particles=[];
let progressUnits=-1;
let spawnQueue=0;
let progressPulseUntil=0;
let lastTs=performance.now();

function resizeCanvas(){
  const r=canvas.getBoundingClientRect(),s=dpr();
  canvas.width=Math.max(1,Math.round(r.width*s));
  canvas.height=Math.max(1,Math.round(r.height*s));
  ctx.setTransform(s,0,0,s,0,0);
}
function corePoint(){
  const cr=core.getBoundingClientRect(),sr=canvas.getBoundingClientRect();
  return {x:cr.left+cr.width/2-sr.left,y:cr.top+cr.height/2-sr.top};
}
function spawnParticle(emphasis=false){
  const cp=corePoint();
  const base=Math.min(canvas.clientWidth,canvas.clientHeight);
  const radius=base*(.14+Math.random()*.23);
  const angle=Math.random()*Math.PI*2;
  particles.push({
    radius,
    angle,
    x:cp.x+Math.cos(angle)*radius,
    y:cp.y+Math.sin(angle)*radius*(.72+Math.random()*.22),
    size:(emphasis?1.3:0.7)+Math.random()*1.8,
    alpha:(emphasis?.45:.18)+Math.random()*.48,
    orbit:(Math.random()<.5?-1:1)*(.00008+Math.random()*.0002),
    phase:Math.random()*Math.PI*2,
    emphasis:emphasis?1:0,
  });
  if(particles.length>1800) particles.splice(0,particles.length-1800);
}
function seedToProgress(progress){
  const target=Math.min(1800,Math.round(progress*1000));
  while(particles.length<target) spawnParticle(false);
}
function readProgress(){
  const n=parseFloat(String(pctEl.textContent||'0').replace('%',''));
  return Number.isFinite(n)?clamp(n):0;
}
function units(){return Math.round(readProgress()*1000)}
function triggerProgressPulse(){
  progressPulseUntil=performance.now()+220;
  stage.classList.remove('progress-step');
  candidate.classList.remove('progress-step');
  void stage.offsetWidth;
  stage.classList.add('progress-step');
  candidate.classList.add('progress-step');
  window.setTimeout(()=>{
    stage.classList.remove('progress-step');
    candidate.classList.remove('progress-step');
  },240);
}
function syncProgress(){
  const progress=readProgress();
  const current=units();
  if(progressUnits<0){
    progressUnits=current;
    seedToProgress(progress);
    return;
  }
  if(current<progressUnits){
    /* New round/reset: clear the old energy field completely. */
    particles=[];
    spawnQueue=0;
    progressUnits=current;
    seedToProgress(progress);
    return;
  }
  const delta=current-progressUnits;
  if(delta>0){
    spawnQueue=Math.min(2400,spawnQueue+delta);
    /* Immediate visible response: the first particle of the step appears now. */
    spawnParticle(true);
    progressUnits=current;
    triggerProgressPulse();
  }
}
function drainQueue(){
  const count=Math.min(18,spawnQueue);
  for(let i=0;i<count;i++) spawnParticle(false);
  spawnQueue-=count;
}
function render(now){
  const w=canvas.clientWidth,h=canvas.clientHeight;
  ctx.clearRect(0,0,w,h);
  const cp=corePoint();
  const pulse=now<progressPulseUntil;
  for(const p of particles){
    p.angle+=p.orbit*(now-lastTs);
    const wobble=1+Math.sin(now*.0012+p.phase)*.018;
    const targetX=cp.x+Math.cos(p.angle)*p.radius*wobble;
    const targetY=cp.y+Math.sin(p.angle)*p.radius*(.72+Math.sin(now*.001+p.phase)*.018);
    p.x+=(targetX-p.x)*.045;
    p.y+=(targetY-p.y)*.045;
    const alpha=p.alpha*(pulse?1.18:1)*(p.emphasis?1.35:1);
    const size=p.size+(pulse?.35:0);
    ctx.beginPath();
    ctx.arc(p.x,p.y,size,0,Math.PI*2);
    ctx.fillStyle=`rgba(95,255,125,${Math.min(.95,alpha)})`;
    ctx.shadowBlur=p.emphasis?12:6;
    ctx.shadowColor=p.emphasis?'rgba(210,255,220,.95)':'rgba(70,255,110,.75)';
    ctx.fill();
  }
  ctx.shadowBlur=0;
}

function tick(now){
  const dt=Math.min(48,now-lastTs);
  /* dt kept for stable frame cadence; particle motion itself is intentionally subtle. */
  lastTs=now;
  void dt;
  syncProgress();
  drainQueue();
  render(now);
  requestAnimationFrame(tick);
}

const progressObserver=new MutationObserver(syncProgress);
progressObserver.observe(pctEl,{characterData:true,childList:true,subtree:true});
window.addEventListener('resize',resizeCanvas,{passive:true});
resizeCanvas();
syncProgress();
requestAnimationFrame(tick);

/* ------------------------------------------------------------------------- */
/* BLOCK FOUND                                                               */
/* ------------------------------------------------------------------------- */
const forge=document.getElementById('forge');
let blockTimer=0;
function blockFound(){
  stage.classList.remove('progress-forged');
  candidate.classList.remove('block-found');
  void stage.offsetWidth;
  stage.classList.add('progress-forged');
  candidate.classList.add('block-found');
  for(let i=0;i<80;i++) spawnParticle(true);
  clearTimeout(blockTimer);
  blockTimer=setTimeout(()=>{
    stage.classList.remove('progress-forged');
    candidate.classList.remove('block-found');
  },3600);
}
const classObserver=new MutationObserver(muts=>{
  for(const m of muts){
    if(m.type!=='attributes'||m.attributeName!=='class') continue;
    const cls=String(stage.className)+' '+String(candidate.className)+' '+String(forge?.className||'');
    if(/hit-block|explode|block-found/.test(cls)){
      blockFound();
      break;
    }
  }
});
classObserver.observe(stage,{attributes:true,attributeFilter:['class']});
classObserver.observe(candidate,{attributes:true,attributeFilter:['class']});
if(forge) classObserver.observe(forge,{attributes:true,attributeFilter:['class']});
})();
