#!/usr/bin/env python3
"""Replace the stylized robot with a high-fidelity articulated industrial miner rig."""
from pathlib import Path

JS = Path('/app/monitor/static/dashboard_v4_miner.js')

code = r'''(()=>{
'use strict';
if(window.__FIXEDCOIN_MINER_PUPPET_V3__)return;
window.__FIXEDCOIN_MINER_PUPPET_V3__=true;
const host=document.getElementById('minerFigure');
if(!host)return;

const svg=`<svg class="miner-puppet miner-puppet-v3" viewBox="0 0 620 500" preserveAspectRatio="xMidYMax meet" aria-label="FIX-ASIC industrial miner forging FixedCoin">
<defs>
 <linearGradient id="v3Suit" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#8aa6ad"/><stop offset=".16" stop-color="#506f78"/><stop offset=".45" stop-color="#172f39"/><stop offset=".78" stop-color="#09171e"/><stop offset="1" stop-color="#02080d"/></linearGradient>
 <linearGradient id="v3SuitDark" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#36545d"/><stop offset=".5" stop-color="#10242d"/><stop offset="1" stop-color="#040c11"/></linearGradient>
 <linearGradient id="v3Helmet" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#b5c8cc"/><stop offset=".18" stop-color="#607f88"/><stop offset=".45" stop-color="#263f48"/><stop offset=".8" stop-color="#0a171d"/><stop offset="1" stop-color="#02070b"/></linearGradient>
 <linearGradient id="v3Metal" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#203b45"/><stop offset=".22" stop-color="#75b4c1"/><stop offset=".48" stop-color="#d7ecef"/><stop offset=".7" stop-color="#66858d"/><stop offset="1" stop-color="#152b33"/></linearGradient>
 <linearGradient id="v3Hammer" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#eef8f8"/><stop offset=".28" stop-color="#9ab4b9"/><stop offset=".65" stop-color="#415a61"/><stop offset="1" stop-color="#172b32"/></linearGradient>
 <radialGradient id="v3Lamp"><stop stop-color="#fffbd2"/><stop offset=".18" stop-color="#a7ffff"/><stop offset=".42" stop-color="#20dff5"/><stop offset="1" stop-color="#0b6f7e" stop-opacity="0"/></radialGradient>
 <radialGradient id="v3Glow"><stop stop-color="#31edff" stop-opacity=".4"/><stop offset="1" stop-color="#31edff" stop-opacity="0"/></radialGradient>
 <linearGradient id="v3Anvil" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#b3c4c7"/><stop offset=".28" stop-color="#657b82"/><stop offset=".62" stop-color="#293d43"/><stop offset="1" stop-color="#0b171c"/></linearGradient>
 <filter id="v3Shadow"><feDropShadow dx="0" dy="18" stdDeviation="14" flood-color="#000" flood-opacity=".72"/></filter>
 <filter id="v3Glow"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <filter id="v3Soft"><feGaussianBlur stdDeviation="15"/></filter>
 <filter id="v3Texture"><feTurbulence type="fractalNoise" baseFrequency=".055" numOctaves="2" seed="7" result="n"/><feColorMatrix in="n" values=".5 0 0 0 .15 .5 0 0 0 .2 .5 0 0 0 .22 0 0 0 .16 0" result="grain"/><feBlend in="SourceGraphic" in2="grain" mode="soft-light"/></filter>
</defs>
<g class="miner-rig-v3" filter="url(#v3Shadow)">
 <ellipse class="miner-ground-shadow" cx="210" cy="468" rx="170" ry="17" fill="#000" opacity=".7"/>
 <g class="v3-backpack"><path d="M86 196Q55 203 55 244V356Q58 377 82 384L112 372V213Z" fill="url(#v3SuitDark)" stroke="#607d85" stroke-width="6"/><path d="M74 228V350M91 216V365" stroke="#1b3b45" stroke-width="10"/><rect x="64" y="267" width="30" height="8" rx="4" fill="#2b5661"/></g>
 <g class="v3-legs">
  <g class="v3-leg-left"><path d="M135 338Q160 347 187 339L184 426Q181 444 163 452H124Q117 438 126 421Z" fill="url(#v3Suit)" stroke="#6d8e96" stroke-width="7"/><path d="M115 443Q137 435 175 445Q190 450 194 466L188 474H102Q99 458 115 443Z" fill="#071319" stroke="#6c898f" stroke-width="7"/></g>
  <g class="v3-leg-right"><path d="M191 338Q218 347 242 337L258 419Q263 439 247 451H211Q197 440 198 421L188 363Z" fill="url(#v3Suit)" stroke="#6d8e96" stroke-width="7"/><path d="M224 442Q250 434 281 447Q295 454 296 468L289 475H210Q207 458 224 442Z" fill="#071319" stroke="#6c898f" stroke-width="7"/></g>
 </g>
 <g class="v3-torso">
  <path d="M112 177Q130 148 168 143L216 145Q253 150 272 181L287 337Q270 356 226 362H158Q115 356 101 334Z" fill="url(#v3Suit)" stroke="#78969d" stroke-width="8" filter="url(#v3Texture)"/>
  <path d="M119 202Q188 221 270 198L276 322Q240 345 153 332Z" fill="#061219" opacity=".62"/>
  <path d="M128 221H263M125 254H269M130 289H272" stroke="#28535e" stroke-width="5" opacity=".8"/>
  <path d="M153 176Q190 188 233 174" stroke="#a6bdc1" stroke-width="5" opacity=".45"/>
  <ellipse cx="190" cy="260" rx="96" ry="110" fill="url(#v3Glow)" opacity=".16"/>
  <text x="190" y="270" text-anchor="middle" fill="#d4e7ea" font-family="JetBrains Mono,monospace" font-size="20" font-weight="800" letter-spacing="4">FIX-ASIC</text>
  <rect x="151" y="300" width="82" height="8" rx="4" fill="#27e7f5" filter="url(#v3Glow)"/>
  <g class="v3-chest-rivets" fill="#9bb4b9"><circle cx="139" cy="225" r="3"/><circle cx="250" cy="218" r="3"/><circle cx="145" cy="318" r="3"/><circle cx="254" cy="314" r="3"/></g>
 </g>
 <g class="v3-head">
  <path d="M110 130Q101 83 127 48Q151 15 193 14Q239 14 263 49Q285 82 278 132L258 164H132Z" fill="url(#v3Helmet)" stroke="#819da4" stroke-width="8"/>
  <path d="M102 67Q118 25 158 10Q208 -8 250 17Q276 32 291 67L281 101Q242 75 196 75Q147 76 107 102Z" fill="url(#v3Metal)" stroke="#9bb3b8" stroke-width="7"/>
  <path d="M121 99Q192 78 271 101L264 139Q240 166 194 167Q146 164 126 140Z" fill="#03090d" stroke="#496a74" stroke-width="7"/>
  <path d="M139 130Q194 114 249 130" stroke="#2de6f7" stroke-width="7" stroke-linecap="round" filter="url(#v3Glow)"/>
  <circle cx="194" cy="48" r="36" fill="url(#v3Lamp)"/>
  <circle cx="194" cy="48" r="12" fill="#fff7bc" filter="url(#v3Glow)"/>
  <path d="M126 159Q193 174 263 158" stroke="#a7bec3" stroke-width="6"/>
  <path d="M147 82Q193 65 246 82" stroke="#d3e2e4" stroke-width="4" opacity=".28"/>
  <g class="v3-head-lamp"><circle cx="194" cy="48" r="8" fill="#fff7c0"/><circle cx="194" cy="48" r="20" fill="none" stroke="#38eaff" stroke-width="2" opacity=".65"/></g>
 </g>
 <g class="v3-back-arm"><path d="M115 189Q85 191 77 222L73 328Q78 350 100 356Q123 349 130 324L139 224Z" fill="url(#v3SuitDark)" stroke="#698991" stroke-width="8"/><path d="M96 226L91 323" stroke="#28525d" stroke-width="10" stroke-linecap="round"/></g>
 <g class="v3-hammer-arm">
  <g class="v3-shoulder"><circle cx="246" cy="189" r="25" fill="#3d5e68" stroke="#91aeb4" stroke-width="7"/><circle cx="246" cy="189" r="10" fill="#142a32" stroke="#63828a" stroke-width="3"/></g>
  <g class="v3-upper-arm"><path d="M245 185Q268 171 291 187L350 225L328 262Q296 236 263 218L235 207Z" fill="url(#v3Suit)" stroke="#79979e" stroke-width="8"/></g>
  <g class="v3-elbow"><circle cx="335" cy="243" r="20" fill="#385963" stroke="#91adb2" stroke-width="6"/></g>
  <g class="v3-forearm"><path d="M333 224L389 242L374 285L317 261Z" fill="url(#v3SuitDark)" stroke="#78979f" stroke-width="8"/><path d="M358 245L386 252L378 276L351 269Z" fill="#4e6c74" stroke="#91abb1" stroke-width="4"/></g>
  <g class="v3-hand"><path d="M373 255Q395 250 410 264L414 281Q403 296 386 289L370 278Z" fill="#6d8990" stroke="#9bb4b9" stroke-width="5"/></g>
  <g class="v3-hammer"><rect x="399" y="254" width="128" height="16" rx="8" fill="url(#v3Metal)"/><path d="M499 215L548 225Q558 228 557 241L551 287Q548 300 536 298L493 288L499 269Z" fill="url(#v3Hammer)" stroke="#a7bec2" stroke-width="7"/><path d="M510 231L546 238" stroke="#f4ffff" stroke-width="5" opacity=".7"/></g>
 </g>
 <g class="v3-antenna"><path d="M257 53V23" stroke="#6f9199" stroke-width="5"/><circle cx="257" cy="18" r="7" fill="#5dff78" filter="url(#v3Glow)"/></g>
</g>
<g class="v3-anvil" transform="translate(342 368)">
 <path d="M-12 20H220L246 38Q249 47 237 53H-31Q-43 46-38 36Z" fill="url(#v3Anvil)" stroke="#8ea7ac" stroke-width="6"/>
 <path d="M58 53H166L178 128H42Z" fill="url(#v3Anvil)" stroke="#789198" stroke-width="6"/>
 <path d="M31 127H192L214 142H9Z" fill="#0a171d" stroke="#607b82" stroke-width="6"/>
 <text x="112" y="48" text-anchor="middle" fill="#dcebed" font-family="JetBrains Mono,monospace" font-size="16" font-weight="800">FIXCOIN</text>
 <path d="M-5 34H55" stroke="#d9ecef" stroke-width="4" opacity=".5"/>
</g>
<g class="v3-forge-glow"><ellipse cx="470" cy="401" rx="105" ry="50" fill="#ffad42" opacity=".12" filter="url(#v3Soft)"/></g>
</svg>`;

host.innerHTML=svg;
const puppet=host.querySelector('.miner-puppet-v3');
const rig=host.querySelector('.miner-rig-v3');
const torso=host.querySelector('.v3-torso');
const head=host.querySelector('.v3-head');
const legs=host.querySelector('.v3-legs');
const shoulder=host.querySelector('.v3-shoulder');
const upper=host.querySelector('.v3-upper-arm');
const elbow=host.querySelector('.v3-elbow');
const fore=host.querySelector('.v3-forearm');
const hand=host.querySelector('.v3-hand');
const hammer=host.querySelector('.v3-hammer');
const anvil=host.querySelector('.v3-anvil');
const lamp=host.querySelector('.v3-head-lamp');
for(const el of [rig,torso,head,legs,shoulder,upper,elbow,fore,hand,hammer])if(el){el.style.transformBox='fill-box';el.style.transformOrigin='center'}
upper.style.transformOrigin='8% 50%'; fore.style.transformOrigin='12% 50%'; hand.style.transformOrigin='20% 50%'; hammer.style.transformOrigin='5% 50%'; shoulder.style.transformOrigin='50% 50%'; elbow.style.transformOrigin='50% 50%';

let idle=[];let strikeId=0;
const reduced=()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches;
function cancelIdle(){idle.forEach(a=>{try{a.cancel()}catch(_){}});idle=[]}
function idleMotion(){if(reduced())return;cancelIdle();idle.push(rig.animate([{transform:'translateY(0) rotate(0)'},{transform:'translateY(-2px) rotate(-.35deg)'},{transform:'translateY(0) rotate(0)'}],{duration:3200,iterations:Infinity,easing:'ease-in-out'}));idle.push(head.animate([{transform:'rotate(-.45deg)'},{transform:'rotate(.45deg)'},{transform:'rotate(-.45deg)'}],{duration:3900,iterations:Infinity,easing:'ease-in-out'}));idle.push(shoulder.animate([{transform:'translateY(0)'},{transform:'translateY(1.5px)'},{transform:'translateY(0)'}],{duration:2400,iterations:Infinity,easing:'ease-in-out'}));}
idleMotion();

function impact(){
 const g=document.createElementNS('http://www.w3.org/2000/svg','g');g.classList.add('v3-impact');g.setAttribute('transform','translate(466 391)');
 g.innerHTML='<circle r="8" fill="#fff6bd"/><circle r="24" fill="none" stroke="#ffd45e" stroke-width="4"/><circle r="46" fill="none" stroke="#ff7638" stroke-width="3" opacity=".8"/><path d="M-58 0H-25M25 0H58M0-58V-25M0 25V58M-40-40L-19-19M19 19L40 40M40-40L19-19M-19 19L-40 40" stroke="#ffe7a4" stroke-width="4" stroke-linecap="round"/>';
 puppet.appendChild(g);g.animate([{opacity:0,transform:'translate(466px,391px) scale(.15)'},{opacity:1,transform:'translate(466px,391px) scale(1)',offset:.2},{opacity:0,transform:'translate(466px,391px) scale(2.7)'}],{duration:430,easing:'cubic-bezier(.08,.85,.15,1)'}).finished.finally(()=>g.remove()).catch(()=>g.remove());
}

function strike(kind='accept'){
 const id=++strikeId;cancelIdle();const reject=kind==='reject';const d=reject?760:1180;const ease='cubic-bezier(.08,.82,.14,1)';
 const body=rig.animate([{transform:'translate(0,0) rotate(0)'},{transform:'translate(-8px,5px) rotate(-3deg)',offset:.32},{transform:'translate(8px,5px) rotate(3deg)',offset:.56},{transform:'translate(1px,1px) rotate(.5deg)',offset:.78},{transform:'translate(0,0) rotate(0)'}],{duration:d,easing:ease,fill:'both'});
 torso.animate([{transform:'rotate(0)'},{transform:'rotate(-4deg)',offset:.32},{transform:'rotate(4deg)',offset:.56},{transform:'rotate(0)'}],{duration:d,easing:ease,fill:'both'});
 legs.animate([{transform:'translate(0,0)'},{transform:'translate(-3px,1px) rotate(-1deg)',offset:.32},{transform:'translate(4px,1px) rotate(1deg)',offset:.56},{transform:'translate(0,0)'}],{duration:d,easing:ease,fill:'both'});
 const raise=reject?-18:-68,drop=reject?16:38;
 upper.animate([{transform:'rotate(6deg)'},{transform:`rotate(${raise}deg) translate(-7px,-9px)`,offset:.34},{transform:`rotate(${drop}deg) translate(9px,10px)`,offset:.57},{transform:'rotate(6deg)'}],{duration:d,easing:ease,fill:'both'});
 fore.animate([{transform:'rotate(5deg)'},{transform:`rotate(${raise+5}deg) translate(-8px,-5px)`,offset:.36},{transform:`rotate(${drop+8}deg) translate(10px,9px)`,offset:.58},{transform:'rotate(5deg)'}],{duration:d,easing:ease,fill:'both'});
 hand.animate([{transform:'rotate(0)'},{transform:'rotate(-8deg)',offset:.35},{transform:'rotate(7deg)',offset:.58},{transform:'rotate(0)'}],{duration:d,easing:ease,fill:'both'});
 hammer.animate([{transform:'rotate(8deg)'},{transform:'rotate(-42deg) translate(-4px,-8px)',offset:.39},{transform:'rotate(31deg) translate(7px,10px)',offset:.59},{transform:'rotate(10deg)',offset:.8},{transform:'rotate(8deg)'}],{duration:d,easing:ease,fill:'both'});
 head.animate([{transform:'rotate(0)'},{transform:'rotate(-2deg) translate(-2px,1px)',offset:.35},{transform:'rotate(2.5deg) translate(3px,1px)',offset:.58},{transform:'rotate(0)'}],{duration:d,easing:ease,fill:'both'});
 lamp.animate([{opacity:.75,transform:'scale(1)'},{opacity:1,transform:'scale(1.15)',offset:.38},{opacity:.75,transform:'scale(1)'}],{duration:d,easing:ease,fill:'both'});
 if(!reject)setTimeout(()=>{if(id===strikeId)impact()},Math.round(d*.59));
 body.finished.finally(()=>{if(id===strikeId)idleMotion()}).catch(()=>{if(id===strikeId)idleMotion()});
}

window.addEventListener('fixedcoin:accept',()=>strike('accept'));
window.addEventListener('fixedcoin:reject',()=>strike('reject'));
window.addEventListener('fixedcoin:block',()=>{strike('accept');setTimeout(impact,80)});
window.fixedcoinMiner={strike,impact};
})();
'''
JS.write_text(code)
print('dashboard miner v3 installed: high-fidelity industrial miner, articulated human-like body/arm/hammer rig, realistic swing timing, anvil impact and no raster image')
'''

JS.write_text(code)
print('dashboard miner v3 installed: high-fidelity industrial miner, articulated human-like body/arm/hammer rig, realistic swing timing, anvil impact and no raster image')
