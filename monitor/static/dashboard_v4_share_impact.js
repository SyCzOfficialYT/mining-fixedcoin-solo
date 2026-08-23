(()=>{
'use strict';
if(window.__FIXEDCOIN_SHARE_IMPACT_V1__)return;
window.__FIXEDCOIN_SHARE_IMPACT_V1__=true;
const forge=document.getElementById('forge');
const accepted=document.getElementById('acceptedCount');
const rejected=document.getElementById('rejectedCount');
if(!forge||!accepted||!rejected)return;

const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const center=el=>{const r=el?.getBoundingClientRect();return r?{x:r.left+r.width/2,y:r.top+r.height/2}:null};
const dot=kind=>center(forge.querySelector(kind==='accept'?'.accepted .event-dot':'.rejected .event-dot'));
const source=()=>center(document.getElementById('impact')||document.getElementById('anvil')||document.getElementById('forgeCore'))||center(forge);
const clearClass=kind=>forge.classList.remove(kind==='accept'?'share-collision-accept':'share-collision-reject');

function cleanup(el){el?.remove()}
function impactFX(kind,p){
  if(!p)return;
  const burst=document.createElement('i');burst.className=`share-impact-burst ${kind}`;burst.style.transform=`translate(${p.x}px,${p.y}px) scale(.4)`;document.body.appendChild(burst);
  const ring=document.createElement('i');ring.className=`share-impact-ring ${kind}`;ring.style.transform=`translate(${p.x}px,${p.y}px) scale(.35)`;document.body.appendChild(ring);
  burst.animate([
    {transform:`translate(${p.x}px,${p.y}px) scale(.35)`,opacity:1},
    {transform:`translate(${p.x}px,${p.y}px) scale(7)`,opacity:0}
  ],{duration:460,easing:'cubic-bezier(.08,.72,.16,1)',fill:'forwards'}).finished.then(()=>cleanup(burst)).catch(()=>cleanup(burst));
  ring.animate([
    {transform:`translate(${p.x}px,${p.y}px) scale(.35)`,opacity:1},
    {transform:`translate(${p.x}px,${p.y}px) scale(5.5)`,opacity:0}
  ],{duration:560,easing:'cubic-bezier(.08,.72,.16,1)',fill:'forwards'}).finished.then(()=>cleanup(ring)).catch(()=>cleanup(ring));

  const count=kind==='accept'?18:24;
  for(let i=0;i<count;i++){
    const shard=document.createElement('i');
    shard.className=`share-impact-burst ${kind}`;
    shard.style.width=(kind==='accept'?2:2.5)+'px';
    shard.style.height=(kind==='accept'?10:13)+'px';
    document.body.appendChild(shard);
    const a=Math.random()*Math.PI*2,dist=28+Math.random()*95,d=.42+Math.random()*.28;
    shard.style.transform=`translate(${p.x}px,${p.y}px) rotate(${a}rad) scale(.8)`;
    shard.animate([
      {transform:`translate(${p.x}px,${p.y}px) rotate(${a}rad) translateY(0) scale(.8)`,opacity:1},
      {transform:`translate(${p.x}px,${p.y}px) rotate(${a}rad) translateY(-${dist}px) scale(.1)`,opacity:0}
    ],{duration:d*1000,easing:'cubic-bezier(.08,.82,.16,1)',fill:'forwards'}).finished.then(()=>cleanup(shard)).catch(()=>cleanup(shard));
  }
}

async function launch(kind){
  const from=source(),to=dot(kind);
  if(!from||!to)return;
  const projectile=document.createElement('i');
  projectile.className=`share-collision-projectile ${kind}`;
  document.body.appendChild(projectile);
  const dx=to.x-from.x,dy=to.y-from.y,dist=Math.hypot(dx,dy);
  const duration=Math.max(360,Math.min(900,dist*1.05));
  const angle=Math.atan2(dy,dx)*180/Math.PI;
  const trail=kind==='accept'?'drop-shadow(0 0 8px #55ff70)':'drop-shadow(0 0 8px #ff4d4d)';
  const animation=projectile.animate([
    {transform:`translate(${from.x}px,${from.y}px) rotate(${angle}deg) scale(.55)`,opacity:.05,filter:trail},
    {transform:`translate(${from.x+dx*.18}px,${from.y+dy*.18}px) rotate(${angle}deg) scale(1.15)`,opacity:1,filter:trail},
    {transform:`translate(${from.x+dx*.78}px,${from.y+dy*.78}px) rotate(${angle}deg) scale(.9)`,opacity:1,filter:trail},
    {transform:`translate(${to.x}px,${to.y}px) rotate(${angle}deg) scale(1.35)`,opacity:1,filter:trail}
  ],{duration,easing:'cubic-bezier(.18,.76,.16,1)',fill:'forwards'});
  try{await animation.finished}catch(_){ }
  cleanup(projectile);
  forge.classList.remove('share-collision-accept','share-collision-reject');
  void forge.offsetWidth;
  forge.classList.add(kind==='accept'?'share-collision-accept':'share-collision-reject');
  impactFX(kind,to);
  await sleep(760);
  clearClass(kind);
}

let lastA=Number(accepted.textContent)||0;
let lastR=Number(rejected.textContent)||0;
let boot=true;
let runningA=0,runningR=0;
const queue=(kind,count)=>{
  const slot=kind==='accept'?'runningA':'runningR';
  const available=kind==='accept'?10-runningA:10-runningR;
  const n=Math.min(count,Math.max(0,available));
  for(let i=0;i<n;i++){
    if(kind==='accept')runningA++;else runningR++;
    launch(kind).finally(()=>{if(kind==='accept')runningA--;else runningR--;});
  }
};
const observer=new MutationObserver(()=>{
  const a=Number(accepted.textContent)||0,r=Number(rejected.textContent)||0;
  if(!boot){if(a>lastA)queue('accept',Math.min(a-lastA,4));if(r>lastR)queue('reject',Math.min(r-lastR,4));}
  lastA=a;lastR=r;boot=false;
});
observer.observe(accepted,{childList:true,characterData:true,subtree:true});
observer.observe(rejected,{childList:true,characterData:true,subtree:true});
})();
