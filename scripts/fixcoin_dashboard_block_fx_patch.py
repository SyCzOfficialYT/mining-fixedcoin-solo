#!/usr/bin/env python3
"""Wire the dashboard's SSE block events to a visible block-found animation.

The backend already emits ``type=block`` for BLOCK CANDIDATE log entries. The
v4 reference UI handled accept/reject events but ignored block events, so a
real candidate could reach 100% without any visual celebration.
"""
from pathlib import Path

JS = Path('/app/monitor/static/dashboard_v4_reference_final.js')
HTML = Path('/app/monitor/templates/dashboard_v4.html')
text = JS.read_text()

if 'FIXEDCOIN_BLOCK_FX_V1' in text:
    print('dashboard block FX already patched')
    raise SystemExit(0)

needle = "const handleLiveEvent=d=>{if(!d||!d.type)return;if(d.type==='accept'){hitCard(acceptedCard,'accept');hitCard(combo,'accept')}else if(d.type==='reject'){hitCard(rejectedCard,'reject')}window.dispatchEvent(new CustomEvent('fixedcoin:live',{detail:d}))};"
if needle not in text:
    raise RuntimeError('dashboard block FX: live event handler anchor not found')

replacement = r'''const blockEvents=new Set();
const blockHit=()=>{
 const forge=document.getElementById('forge'),candidate=document.getElementById('candidate'),core=document.getElementById('candidateCore');
 const replay=(el,frames,opts)=>{if(!el||typeof el.animate!=='function')return;try{el.animate(frames,opts)}catch(_) {}};
 if(forge){forge.classList.remove('hit-block');void forge.offsetWidth;forge.classList.add('hit-block');setTimeout(()=>forge.classList.remove('hit-block'),1650)}
 if(candidate){candidate.classList.remove('block-found');void candidate.offsetWidth;candidate.classList.add('block-found');setTimeout(()=>candidate.classList.remove('block-found'),1800)}
 replay(core,[{transform:'scale(1)',filter:'brightness(1)'},{transform:'scale(1.18)',filter:'brightness(1.8)'},{transform:'scale(1.06)',filter:'brightness(1.35)'},{transform:'scale(1)',filter:'brightness(1)'}],{duration:1100,easing:'cubic-bezier(.12,.8,.18,1)'});
 const stage=document.getElementById('forgeStage')||candidate||document.body;
 const r=stage.getBoundingClientRect(),cx=r.left+r.width*.5,cy=r.top+r.height*.5;
 for(let i=0;i<72;i++){
  const spark=document.createElement('i');spark.className='block-found-spark';
  Object.assign(spark.style,{position:'fixed',left:cx+'px',top:cy+'px',width:(2+Math.random()*4)+'px',height:(2+Math.random()*4)+'px',borderRadius:'50%',pointerEvents:'none',zIndex:'9999',background:i%3===0?'#ffcf5a':i%3===1?'#55ff91':'#28dfff',boxShadow:'0 0 12px currentColor,0 0 24px currentColor'});
  document.body.appendChild(spark);
  const a=Math.random()*Math.PI*2,d=90+Math.random()*340;
  spark.animate([{transform:'translate(-50%,-50%) scale(1.7)',opacity:1},{transform:`translate(calc(-50% + ${Math.cos(a)*d}px),calc(-50% + ${Math.sin(a)*d}px)) scale(0)`,opacity:0}],{duration:750+Math.random()*850,easing:'cubic-bezier(.08,.82,.16,1)'}).finished.finally(()=>spark.remove()).catch(()=>spark.remove());
 }
 const banner=document.createElement('div');banner.className='block-found-banner';banner.textContent='✦ BLOCK CANDIDATE FOUND ✦';
 Object.assign(banner.style,{position:'fixed',left:'50%',top:'50%',transform:'translate(-50%,-50%) scale(.72)',zIndex:'10000',pointerEvents:'none',font:'800 clamp(16px,2vw,30px)/1 "JetBrains Mono",monospace',letterSpacing:'.16em',textAlign:'center',color:'#d9ffe5',textShadow:'0 0 10px #55ff91,0 0 28px rgba(40,223,255,.8)',whiteSpace:'nowrap',opacity:'0'});
 document.body.appendChild(banner);
 banner.animate([{opacity:0,transform:'translate(-50%,-50%) scale(.72)'},{opacity:1,transform:'translate(-50%,-50%) scale(1.04)',offset:.28},{opacity:1,transform:'translate(-50%,-50%) scale(1)',offset:.55},{opacity:0,transform:'translate(-50%,-50%) scale(1.08)'}],{duration:1800,easing:'cubic-bezier(.16,.84,.22,1)'}).finished.finally(()=>banner.remove()).catch(()=>banner.remove());
};
const handleLiveEvent=d=>{
 if(!d||!d.type)return;
 if(d.type==='accept'){hitCard(acceptedCard,'accept');hitCard(combo,'accept')}
 else if(d.type==='reject'){hitCard(rejectedCard,'reject')}
 else if(d.type==='block'){
  const key=String(d.ts||'')+'|'+String(d.message||'');
  if(blockEvents.has(key))return;
  blockEvents.add(key);if(blockEvents.size>64)blockEvents.delete(blockEvents.values().next().value);
  blockHit();window.dispatchEvent(new CustomEvent('fixedcoin:block',{detail:d}));
 }
 window.dispatchEvent(new CustomEvent('fixedcoin:live',{detail:d}))
};
/* FIXEDCOIN_BLOCK_FX_V1 */'''

text = text.replace(needle, replacement, 1)
JS.write_text(text)

html = HTML.read_text()
old = '/static/dashboard_v4_reference_final.js?v=20260826-mythic1'
new = '/static/dashboard_v4_reference_final.js?v=20260827-blockfx1'
if old in html:
    html = html.replace(old, new, 1)
else:
    raise RuntimeError('dashboard block FX: reference JS cache marker not found')
HTML.write_text(html)

print('dashboard block FX applied: SSE block events now trigger forge/candidate celebration')
