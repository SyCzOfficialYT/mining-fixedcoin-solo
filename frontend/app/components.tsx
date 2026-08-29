'use client';

import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';
import { Activity, Blocks, CircleDollarSign, Cpu, Gauge, Gem, Hammer, History, LayoutDashboard, Network, Settings, ShieldCheck, Sparkles, Users, Wallet } from 'lucide-react';

export const navItems: ReadonlyArray<readonly [string, LucideIcon]> = [
  ['Dashboard', LayoutDashboard], ['Mining', Hammer], ['Shares', Activity], ['Blocks', Blocks],
  ['Workers', Users], ['Settings', Settings], ['Logs', History], ['System', Network],
];

export function OrnateCorners(){return <><span className="corner corner-tl"/><span className="corner corner-tr"/><span className="corner corner-bl"/><span className="corner corner-br"/></>}

export function Dragon({side}:{side:'left'|'right'}){
  const id=`dragon-${side}`;
  const flip=side==='right'?'scaleX(-1)':undefined;
  const body=side==='left'?'#2b0b4b':'#062d42';
  const mid=side==='left'?'#6e2a9b':'#12627d';
  const glow=side==='left'?'#c56cff':'#56d9ff';
  const edge=side==='left'?'#e4b4ff':'#9beaff';
  return <svg className={`dragon dragon-${side}`} viewBox="0 0 260 360" style={{transform:flip}} aria-hidden="true">
    <defs>
      <linearGradient id={`${id}-body`} x1="0" y1="0" x2="1" y2="1"><stop stopColor={body}/><stop offset=".34" stopColor={mid}/><stop offset=".72" stopColor="#120c20"/><stop offset="1" stopColor="#03030a"/></linearGradient>
      <linearGradient id={`${id}-wing`} x1="0" y1="0" x2="1" y2="1"><stop stopColor={glow} stopOpacity=".72"/><stop offset=".55" stopColor={mid} stopOpacity=".35"/><stop offset="1" stopColor="#020208" stopOpacity=".08"/></linearGradient>
      <radialGradient id={`${id}-scale`}><stop stopColor="#fff" stopOpacity=".45"/><stop offset=".35" stopColor={glow} stopOpacity=".22"/><stop offset="1" stopColor="#000" stopOpacity="0"/></radialGradient>
      <filter id={`${id}-glow`} x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1.8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      <filter id={`${id}-texture`} x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="2" seed={side==='left'?7:11} result="n"/><feColorMatrix in="n" type="saturate" values="0" result="g"/><feComponentTransfer in="g"><feFuncA type="table" tableValues="0 .22"/></feComponentTransfer><feBlend in="SourceGraphic" in2="g" mode="screen"/></filter>
    </defs>
    <g opacity=".28" fill="none" stroke={glow}><ellipse cx="128" cy="190" rx="116" ry="78" transform="rotate(-18 128 190)"/><path d="M21 337C46 286 62 239 95 203M40 351C79 302 101 245 122 194M205 337C177 288 166 245 151 198"/></g>
    <g filter={`url(#${id}-glow)`}><g filter={`url(#${id}-texture)`}>
      <path d="M80 342C45 325 32 292 48 266C61 244 91 235 100 209C110 180 87 164 90 132C94 91 130 55 177 48C158 70 157 91 174 104C191 117 220 110 236 129C252 148 247 174 227 188C207 202 180 196 174 220C168 246 198 260 208 287C219 318 193 343 160 352C133 359 104 355 80 342Z" fill={`url(#${id}-body)`} stroke={edge} strokeWidth="2.4"/>
      <path d="M154 104C119 65 79 44 34 42L75 83L45 122L108 105L151 132Z" fill={`url(#${id}-wing)`} stroke={edge} strokeWidth="2.1"/>
      <path d="M168 105C197 66 226 47 254 42L226 82L247 119L195 105L165 130Z" fill={`url(#${id}-wing)`} stroke={edge} strokeWidth="2.1"/>
      <path d="M153 106C165 88 184 78 202 84C220 90 228 106 224 121C219 139 199 149 181 143C166 138 158 126 161 115" fill="none" stroke={edge} strokeWidth="3.2"/>
      <path d="M164 105L154 67L139 86L128 52L119 94M205 108L220 69L231 89L246 55L247 103" fill="none" stroke={edge} strokeWidth="2.8" strokeLinejoin="round"/>
      <path d="M201 119C213 115 223 117 231 124" fill="none" stroke={edge} strokeWidth="1.8"/>
      <circle cx="205" cy="116" r="5.5" fill="#fff" stroke={glow} strokeWidth="2.6"/><circle cx="206" cy="116" r="1.6" fill="#09020f"/>
      <path d="M222 137C237 148 245 162 249 178M218 147C235 163 244 179 247 197M213 160C229 181 237 198 238 217" fill="none" stroke={edge} strokeWidth="1.2" opacity=".72"/>
      <g fill="none" stroke={glow} strokeWidth="1.6" opacity=".62"><path d="M91 179C116 192 141 193 163 183"/><path d="M78 207C110 222 141 222 169 208"/><path d="M69 236C103 251 139 252 173 237"/><path d="M70 266C103 279 137 281 170 268"/><path d="M80 296C108 306 136 308 163 298"/><path d="M98 322C121 330 143 331 157 326"/></g>
      <g fill="none" stroke={edge} strokeWidth="1.2" opacity=".72"><path d="M98 178l-18 18 27-7M123 184l-14 23 27-16M149 184l-7 24 23-18M173 182l5 22 17-16"/><path d="M84 208l-18 20 28-7M112 215l-13 22 27-14M142 215l-5 24 23-18M168 211l8 20 18-14"/><path d="M78 239l-14 18 25-6M108 246l-9 22 25-14M138 246l-2 22 22-17M164 241l8 20 17-14"/></g>
      <ellipse cx="132" cy="210" rx="75" ry="92" fill={`url(#${id}-scale)`} opacity=".22"/><path d="M57 323C88 345 128 351 164 339C184 332 199 319 207 301" fill="none" stroke={edge} strokeWidth="4" opacity=".24"/><path d="M48 336C79 355 122 360 164 350" fill="none" stroke={glow} strokeWidth="1.4" opacity=".5"/>
    </g></g>
  </svg>
}

export function Crystal({large=false}:{large?:boolean}){
  return <div className={`crystal-stage ${large?'crystal-stage-large':''}`}>
    <div className="magic-stars"/><div className="orbit orbit-a"/><div className="orbit orbit-b"/><div className="orbit orbit-c"/>
    <div className="rune-ring rune-ring-a">✦ · ◇ · ✧ · ◇ · ✦ · ◇ · ✧</div><div className="rune-ring rune-ring-b">ᛉ · ✧ · ᛟ · ✦ · ᛉ · ✧</div>
    <motion.div className="crystal-aura" animate={{scale:[.9,1.08,.9],opacity:[.3,.78,.3]}} transition={{duration:4.5,repeat:Infinity,ease:'easeInOut'}}/>
    <motion.div className="crystal-core" animate={{y:[0,-8,0],rotateY:[0,180,360]}} transition={{duration:8,repeat:Infinity,ease:'easeInOut'}}>
      <div className="crystal-face crystal-front"><span>✦</span><i/><b/><em/><u/></div><div className="crystal-face crystal-back"><span>◆</span><i/><b/><em/><u/></div>
    </motion.div><div className="crystal-pedestal"><span/><i/><b/></div>
  </div>
}

export function ScaleArt(){return <svg className="scale-art" viewBox="0 0 360 280" aria-hidden="true"><defs><linearGradient id="gold-scale" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#fff1a3"/><stop offset=".45" stopColor="#d59a2f"/><stop offset="1" stopColor="#6a410e"/></linearGradient></defs><g fill="none" stroke="url(#gold-scale)"><path d="M180 24v214M139 238h82M107 257h146" strokeWidth="7" strokeLinecap="round"/><circle cx="180" cy="28" r="14" fill="#100c17" stroke="#ffd96a" strokeWidth="3"/><path d="M58 76h244M86 76 45 158q41 32 82 0L86 76M274 76l41 82q-41 32-82 0l41-82" strokeWidth="5"/><path d="M45 158q41 18 82 0M233 158q41 18 82 0" strokeWidth="3" opacity=".6"/></g><circle cx="86" cy="76" r="6" fill="#ffe68b"/><circle cx="274" cy="76" r="6" fill="#ffe68b"/><path d="M180 46l9 17h-18zM180 195l-10 18h20z" fill="#e5b84e" opacity=".65"/></svg>}

export function Panel({title,subtitle,children,className='',icon:Icon=Sparkles}:{title:string;subtitle?:string;children:ReactNode;className?:string;icon?:LucideIcon}){return <section className={`magic-panel ${className}`}><OrnateCorners/><div className="panel-heading"><div><h2>{title}</h2>{subtitle&&<p>{subtitle}</p>}</div><Icon size={16}/></div>{children}</section>}
export function MetricCard({label,value,note,tone='violet',icon:Icon=Gauge}:{label:string;value:string;note?:string;tone?:string;icon?:LucideIcon}){return <div className={`metric-card tone-${tone}`}><div className="metric-icon"><Icon size={15}/></div><span>{label}</span><strong>{value}</strong>{note&&<small>{note}</small>}<div className="sparkline"><i/><i/><i/><i/><i/><i/><i/><i/></div></div>}
export function SideStat({label,value,note,tone='violet',icon:Icon=Activity}:{label:string;value:string;note?:string;tone?:string;icon?:LucideIcon}){return <div className={`side-stat tone-${tone}`}><div className="side-stat-icon"><Icon size={15}/></div><span>{label}</span><strong>{value}</strong><small>{note||'LIVE TELEMETRY'}</small></div>}
export function ProgressLine({value,tone='violet'}:{value:number;tone?:string}){return <div className={`magic-progress tone-${tone}`}><i style={{width:`${Math.max(0,Math.min(100,value))}%`}}/></div>}
export function LiveBadge({degraded=false}:{degraded?:boolean}){return <span className={`live-badge ${degraded?'degraded':''}`}><i/>{degraded?'API DEGRADED':'STRATUM · LIVE'}</span>}
export function BrandMark(){return <div className="brand-mark"><Gem size={22}/><span>FIXEDCOIN<small>SOLO NODE</small></span></div>}
export function StatusPill({children}:{children:ReactNode}){return <span className="badge badge-success badge-outline status-pill"><ShieldCheck size={13}/>{children}</span>}
export function DataIcon({kind}:{kind:'wallet'|'cpu'|'network'|'blocks'}){const map={wallet:Wallet,cpu:Cpu,network:Network,blocks:Blocks} as const;const Icon=map[kind];return <Icon size={15}/>}
export function DollarIcon(){return <CircleDollarSign size={15}/>} 
