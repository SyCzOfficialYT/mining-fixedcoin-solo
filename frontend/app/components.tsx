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

/** Real generated dragon artwork from public/reference. */
export function Dragon({side}:{side:'left'|'right'}){
  const src=side==='left'?'/reference/left-dragon.webp':'/reference/right-dragon.svg';
  return <img className={`dragon dragon-${side}`} src={src} alt="" aria-hidden="true" draggable={false}/>;
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
