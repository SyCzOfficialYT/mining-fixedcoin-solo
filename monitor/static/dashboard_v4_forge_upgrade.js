(()=>{
'use strict';
if(window.__FIXEDCOIN_FORGE_UPGRADE_V3__) return;
window.__FIXEDCOIN_FORGE_UPGRADE_V3__=true;
const stage=document.getElementById('forgeStage');
const core=document.getElementById('forgeCore');
const candidate=document.getElementById('candidate');
const pctEl=document.getElementById('candidatePct');
if(!stage||!core||!candidate||!pctEl)return;
const dpr=()=>Math.min(2,window.devicePixelRatio||1),clamp=(n,a=0,b=100)=>Math.max(a,Math.min(b,Number(n)||0));
const canvas=document.createElement('canvas');canvas.className='progress-particle-canvas';canvas.setAttribute('aria-hidden','true');stage.appendChild(canvas);
const ctx=canvas.getContext('2d',{alpha:true});let particles=[],progressUnits=-1,spawnQueue=0,progressPulseUntil=0,lastTs=performance.now();
function resizeCanvas(){const r=canvas.getBoundingClientRect(),s=dpr();canvas.width=Math.max(1,Math.round(r.width*s));canvas.height=Math.max(1,Math.round(r.height*s));ctx.setTransform(s,0,0,s,0,0)}
function corePoint(){const cr=core.getBoundingClientRect(),sr=canvas.getBoundingClientRect();return{x:cr.left+cr.width/2-sr.left,y:cr.top+cr.height/2-sr.top}}
function spawnParticle(emphasis=false){const cp=corePoint(),base=Math.min(canvas.clientWidth,canvas.clientHeight),radius=base*(.14+Math.random()*.23),angle=Math.random()*Math.PI*2;particles.push({radius,angle,x:cp.x+Math.cos(angle)*radius,y:cp.y+Math.sin(angle)*radius*.8,size:(emphasis?1.2:.65)+Math.random()*1.9,alpha:(emphasis?.42:.16)+Math.random()*.5,orbit:(Math.random()<.5?-1:1)*(.00055+Math.random()*.0009),ellipse:.68+Math.random()*.28,drift:(Math.random()-.5)*.00005,phase:Math.random()*Math.PI*2,emphasis:emphasis?1:0});if(particles.length>1800)particles.splice(0,particles.length-1800)}
function seedToProgress(progress){const target=Math.min(1800,Math.round(progress*1000));while(particles.length<target)spawnParticle(false)}
function readProgress(){const n=parseFloat(String(pctEl.textContent||'0').replace('%',''));return Number.isFinite(n)?clamp(n):0}
function units(){return Math.round(readProgress()*1000)}
function triggerProgressPulse(){progressPulseUntil=performance.now()+180;stage.classList.remove('progress-step');candidate.classList.remove('progress-step');void stage.offsetWidth;stage.classList.add('progress-step');candidate.classList.add('progress-step');window.setTimeout(()=>{stage.classList.remove('progress-step');candidate.classList.remove('progress-step')},200)}
function syncProgress(){const progress=readProgress(),current=units();if(progressUnits<0){progressUnits=current;seedToProgress(progress);return}if(current<progressUnits){particles=[];spawnQueue=0;progressUnits=current;seedToProgress(progress);return}const delta=current-progressUnits;if(delta>0){spawnQueue=Math.min(2400,spawnQueue+delta);spawnParticle(true);progressUnits=current;triggerProgressPulse()}}
function drainQueue(){const count=Math.min(16,spawnQueue);for(let i=0;i<count;i++)spawnParticle(false);spawnQueue-=count}
function render(now){const w=canvas.clientWidth,h=canvas.clientHeight;ctx.clearRect(0,0,w,h);const cp=corePoint(),frame=Math.min(48,Math.max(1,now-lastTs)),pulse=now<progressPulseUntil;for(const p of particles){p.angle+=p.orbit*frame;p.radius+=p.drift*frame*1000;const breathe=1+Math.sin(now*.00115+p.phase)*.04;const radial=1+Math.sin(now*.00155+p.phase*1.7)*.055;const targetX=cp.x+Math.cos(p.angle)*p.radius*breathe*radial;const targetY=cp.y+Math.sin(p.angle)*p.radius*(p.ellipse+Math.sin(now*.0011+p.phase)*.025)*radial;const follow=1-Math.pow(.0008,frame/16.67);p.x+=(targetX-p.x)*follow;p.y+=(targetY-p.y)*follow;const microX=Math.sin(now*.0014+p.phase)*3,microY=Math.cos(now*.00125+p.phase)*2.3,alpha=p.alpha*(pulse?1.16:1)*(p.emphasis?1.3:1),size=p.size+(pulse?.3:0);ctx.beginPath();ctx.arc(p.x+microX,p.y+microY,size,0,Math.PI*2);ctx.fillStyle=`rgba(95,255,125,${Math.min(.92,alpha)})`;ctx.shadowBlur=p.emphasis?11:5;ctx.shadowColor=p.emphasis?'rgba(210,255,220,.9)':'rgba(70,255,110,.7)';ctx.fill()}ctx.shadowBlur=0}
function tick(now){lastTs=now;syncProgress();drainQueue();render(now);requestAnimationFrame(tick)}
const progressObserver=new MutationObserver(syncProgress);progressObserver.observe(pctEl,{characterData:true,childList:true,subtree:true});window.addEventListener('resize',resizeCanvas,{passive:true});resizeCanvas();syncProgress();requestAnimationFrame(tick);
const forge=document.getElementById('forge');let blockTimer=0;function blockFound(){stage.classList.remove('progress-forged');candidate.classList.remove('block-found');void stage.offsetWidth;stage.classList.add('progress-forged');candidate.classList.add('block-found');for(let i=0;i<80;i++)spawnParticle(true);clearTimeout(blockTimer);blockTimer=setTimeout(()=>{stage.classList.remove('progress-forged');candidate.classList.remove('block-found')},3600)}
const classObserver=new MutationObserver(muts=>{for(const m of muts){if(m.type!=='attributes'||m.attributeName!=='class')continue;const cls=String(stage.className)+' '+String(candidate.className)+' '+String(forge?.className||'');if(/hit-block|explode|block-found/.test(cls)){blockFound();break}}});classObserver.observe(stage,{attributes:true,attributeFilter:['class']});classObserver.observe(candidate,{attributes:true,attributeFilter:['class']});if(forge)classObserver.observe(forge,{attributes:true,attributeFilter:['class']});
})();
