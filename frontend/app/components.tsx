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

/** Detailed reference-style dragon artwork. Kept as vector markup so it cannot break
 * because of a truncated/corrupt base64 image asset in the public folder. */
export function Dragon({side}:{side:'left'|'right'}){
  const flip=side==='right'?'scaleX(-1)':undefined;
  const id=`dragon-${side}`;
  const body=side==='left'?'#d28aff':'#73dcff';
  const deep=side==='left'?'#26104d':'#092c4c';
  const edge=side==='left'?'#dba0ff':'#6fdcff';
  return <svg className={`dragon dragon-${side}`} viewBox="0 0 420 430" style={{transform:flip}} aria-hidden="true" preserveAspectRatio="xMidYMid meet">
    <defs>
      <linearGradient id={`${id}-body`} x1="0" y1="0" x2="1" y2="1"><stop stopColor={body}/><stop offset=".25" stopColor={side==='left'?'#7626b5':'#1b759f'}/><stop offset=".68" stopColor={deep}/><stop offset="1" stopColor="#03020a"/></linearGradient>
      <linearGradient id={`${id}-edge`} x1="0" y1="0" x2="1" y2="1"><stop stopColor="#fff"/><stop offset=".25" stopColor={edge}/><stop offset=".75" stopColor={side==='left'?'#7b2fb5':'#267fa6'}/><stop offset="1" stopColor="#11182e"/></linearGradient>
      <radialGradient id={`${id}-halo`}><stop stopColor={side==='left'?'#b94cff':'#37caff'} stopOpacity=".34"/><stop offset="1" stopColor="#000" stopOpacity="0"/></radialGradient>
      <filter id={`${id}-glow`}><feGaussianBlur stdDeviation="2.6" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    </defs>
    <ellipse cx="210" cy="218" rx="205" ry="190" fill={`url(#${id}-halo)`} opacity=".55"/>
    <g fill="none" stroke={edge} opacity=".3">
      <ellipse cx="208" cy="217" rx="193" ry="111" transform="rotate(-18 208 217)"/>
      <ellipse cx="208" cy="217" rx="171" ry="91" transform="rotate(24 208 217)"/>
      <ellipse cx="208" cy="217" rx="151" ry="75" transform="rotate(-41 208 217)"/>
    </g>
    <g filter={`url(#${id}-glow)`}>
      <path d="M92 403c-31-33-38-70-18-101 19-30 58-36 66-70 7-29-12-50-1-82 13-38 49-62 92-76-19 25-21 47-5 59 17 13 47 4 69 17 27 15 34 45 20 69-16 27-53 34-55 67-2 37 49 55 58 92 9 38-15 70-54 89-39 19-100 21-172 5z" fill={`url(#${id}-body)`} stroke={`url(#${id}-edge)`} strokeWidth="2.8"/>
      <path d="M125 119 44 55l72 20 43-67 7 88M251 124l91-70-74 18-43-61-5 87" fill={`url(#${id}-body)`} stroke={`url(#${id}-edge)`} strokeWidth="4" strokeLinejoin="round"/>
      <path d="M135 115c25-21 50-31 75-27 28 5 42 27 36 48-5 18-27 31-44 25-18-6-23-26-11-40" fill="none" stroke={`url(#${id}-edge)`} strokeWidth="4"/>
      <path d="M109 137c17-12 38-17 58-14M91 154c18-9 38-12 57-9" fill="none" stroke={edge} strokeWidth="2" opacity=".7"/>
      <circle cx="221" cy="128" r="6.5" fill="#fff" stroke={edge} strokeWidth="3"/>
      <path d="M97 194c38 23 79 26 119 7M86 231c48 26 96 27 143 5M82 270c49 24 101 27 150 6M91 310c43 21 89 23 132 6M111 349c36 16 73 17 108 5" fill="none" stroke={edge} strokeWidth="2.2" opacity=".55"/>
      <path d="M119 170l-27 18 34 4M145 161l-21 26 35-8M176 154l-13 29 29-17M207 154l-3 28 22-24" fill="none" stroke={side==='left'?'#e0b4ff':'#8eeaff'} strokeWidth="2" opacity=".72"/>
      <path d="M116 208l-20 12 24 5M109 247l-22 12 27 4M108 286l-18 11 25 5M119 326l-15 9 23 5M140 361l-11 8 20 3" fill="none" stroke={edge} strokeWidth="1.6" opacity=".65"/>
      <path d="M112 385c48 21 102 22 154-5" fill="none" stroke={side==='left'?'#9d4dd2':'#287ca9'} strokeWidth="7" opacity=".42"/>
      <path d="M96 395c34 10 68 13 101 9" fill="none" stroke="#fff" strokeWidth="1" opacity=".2"/>
    </g>
  </svg>
}

export function Crystal({large=false}:{large?:boolean}){
  return <div className={`crystal-stage ${large?'crystal-stage-large':''}`}>
    <div className="magic-stars"/><div className="orbit orbit-a"/><div className="orbit orbit-b"/><div className="orbit orbit-c"/>
    <div className="rune-ring rune-ring-a">✦ · ◇ · ✧ · ◇ · ✦ · ◇ · ✧</div><div className="rune-ring rune-ring-b">ᛉ · ✧ · ᛟ · ✦ · ᛉ · ✧</div>
    <motion.div className="crystal-aura" animate={{scale:[.88,1.1,.88],opacity:[.28,.82,.28]}} transition={{duration:4.5,repeat:Infinity,ease:'easeInOut'}}/>
    <motion.div className="crystal-core" animate={{y:[0,-9,0],rotateY:[0,180,360]}} transition={{duration:8,repeat:Infinity,ease:'easeInOut'}}>
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
