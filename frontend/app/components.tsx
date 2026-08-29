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
  const flip=side==='right'?'scaleX(-1)':undefined;
  const id=`dragon-${side}`;
  return <svg className={`dragon dragon-${side}`} viewBox="0 0 420 430" style={{transform:flip}} aria-hidden="true">
    <defs>
      <linearGradient id={`${id}-body`} x1="0" y1="0" x2="1" y2="1"><stop stopColor={side==='left'?'#d28aff':'#73dcff'}/><stop offset=".28" stopColor={side==='left'?'#7b27ba':'#1b77a4'}/><stop offset=".7" stopColor={side==='left'?'#26104d':'#092c4c'}/><stop offset="1" stopColor="#04030c"/></linearGradient>
      <linearGradient id={`${id}-edge`} x1="0" y1="0" x2="1" y2="1"><stop stopColor={side==='left'?'#f0c9ff':'#b7efff'}/><stop offset=".5" stopColor={side==='left'?'#8f43d0':'#38bde9'}/><stop offset="1" stopColor="#17203a"/></linearGradient>
      <filter id={`${id}-glow`}><feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    </defs>
    <g opacity=".42" fill="none" stroke={side==='left'?'#b45cff':'#4ccfff'}>
      <ellipse cx="210" cy="214" rx="195" ry="112" transform="rotate(-18 210 214)"/>
      <ellipse cx="210" cy="214" rx="172" ry="91" transform="rotate(25 210 214)"/>
    </g>
    <g filter={`url(#${id}-glow)`}>
      <path d="M92 403c-31-33-38-70-18-101 19-30 58-36 66-70 7-29-12-50-1-82 13-38 49-62 92-76-19 25-21 47-5 59 17 13 47 4 69 17 27 15 34 45 20 69-16 27-53 34-55 67-2 37 49 55 58 92 9 38-15 70-54 89-39 19-100 21-172 5z" fill={`url(#${id}-body)`} stroke={`url(#${id}-edge)`} strokeWidth="2.4"/>
      <path d="M125 119 44 55l72 20 43-67 7 88M251 124l91-70-74 18-43-61-5 87" fill={`url(#${id}-body)`} stroke={`url(#${id}-edge)`} strokeWidth="4" strokeLinejoin="round"/>
      <path d="M135 115c25-21 50-31 75-27 28 5 42 27 36 48-5 18-27 31-44 25-18-6-23-26-11-40" fill="none" stroke={`url(#${id}-edge)`} strokeWidth="4"/>
      <circle cx="221" cy="128" r="6.5" fill="#fff" stroke={side==='left'?'#d596ff':'#86eaff'} strokeWidth="3"/>
      <path d="M97 194c38 23 79 26 119 7M86 231c48 26 96 27 143 5M82 270c49 24 101 27 150 6M91 310c43 21 89 23 132 6M111 349c36 16 73 17 108 5" fill="none" stroke={side==='left'?'#b75cff':'#3ab8e7'} strokeWidth="2" opacity=".48"/>
      <path d="M119 170l-27 18 34 4M145 161l-21 26 35-8M176 154l-13 29 29-17M207 154l-3 28 22-24" fill="none" stroke={side==='left'?'#d19aff':'#78ddff'} strokeWidth="2" opacity=".65"/>
      <path d="M112 385c48 21 102 22 154-5" fill="none" stroke={side==='left'?'#9d4dd2':'#287ca9'} strokeWidth="7" opacity=".38"/>
    </g>
  </svg>
}

export function Crystal({large=false}:{large?:boolean}){
  return <div className={`crystal-stage ${large?'crystal-stage-large':''}`}>
    <div className="magic-stars"/><div className="orbit orbit-a"/><div className="orbit orbit-b"/><div className="orbit orbit-c"/>
    <div className="rune-ring rune-ring-a">✦ · ◇ · ✧ · ◇ · ✦</div><div className="rune-ring rune-ring-b">ᛉ · ✧ · ᛟ · ✦ · ᛉ</div>
    <motion.div className="crystal-aura" animate={{scale:[.92,1.08,.92],opacity:[.35,.78,.35]}} transition={{duration:4.5,repeat:Infinity,ease:'easeInOut'}}/>
    <motion.div className="crystal-core" animate={{y:[0,-8,0],rotateY:[0,180,360]}} transition={{duration:8,repeat:Infinity,ease:'easeInOut'}}>
      <div className="crystal-face crystal-front"><span>✦</span><i/><b/></div><div className="crystal-face crystal-back"><span>◆</span><i/><b/></div>
    </motion.div>
    <div className="crystal-pedestal"><span/><i/><b/></div>
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
