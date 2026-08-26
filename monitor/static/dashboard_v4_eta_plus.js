(()=>{
'use strict';
const etaEl=document.getElementById('eta');
const plus=document.getElementById('etaPlus');
if(!etaEl||!plus)return;
let over=false;
let colorTimer=0;
const update=async()=>{
  try{
    const r=await fetch('/api/status?eta_plus='+Date.now(),{cache:'no-store'});
    if(!r.ok)return;
    const s=await r.json();
    const m=s.mining||{}, n=s.node||{}, round=s.round||{};
    const diff=Number(n.difficulty||round.difficulty||0);
    const hs=Number(m.hashrate_5m)||0;
    const eta=hs>0&&diff>0?diff*4294967296/hs:0;
    const next=eta>600;
    if(next!==over){
      over=next;
      plus.classList.toggle('is-over',over);
      if(!over){plus.classList.remove('is-bordeaux','is-black');clearInterval(colorTimer);colorTimer=0;}
      else if(!colorTimer){
        let i=0;
        const colors=['','is-bordeaux','is-black'];
        const cycle=()=>{plus.classList.remove('is-bordeaux','is-black');plus.classList.add(colors[i%colors.length]);i++;};
        cycle();
        colorTimer=setInterval(cycle,1800);
      }
    }
  }catch(_){ }
};
update();
setInterval(update,3000);
})();
