(()=>{
'use strict';
/* v4: visual state bridge only. Particle/progress rendering is handled by the
   single canvas compositor in dashboard_v4_animation_perf.js. */
if(window.__FIXEDCOIN_FORGE_UPGRADE_V4__)return;
window.__FIXEDCOIN_FORGE_UPGRADE_V4__=true;
const stage=document.getElementById('forgeStage');
const candidate=document.getElementById('candidate');
const forge=document.getElementById('forge');
if(!stage||!candidate)return;
let timer=0;
function blockFound(){
  stage.classList.remove('progress-forged');
  candidate.classList.remove('block-found');
  void stage.offsetWidth;
  stage.classList.add('progress-forged');
  candidate.classList.add('block-found');
  clearTimeout(timer);
  timer=setTimeout(()=>{
    stage.classList.remove('progress-forged');
    candidate.classList.remove('block-found');
  },3600);
}
const observer=new MutationObserver(muts=>{
  for(const m of muts){
    if(m.type!=='attributes'||m.attributeName!=='class')continue;
    const cls=`${stage.className} ${candidate.className} ${forge?.className||''}`;
    if(/hit-block|explode|block-found/.test(cls)){blockFound();break}
  }
});
observer.observe(stage,{attributes:true,attributeFilter:['class']});
observer.observe(candidate,{attributes:true,attributeFilter:['class']});
if(forge)observer.observe(forge,{attributes:true,attributeFilter:['class']});
})();
