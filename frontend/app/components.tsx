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
  const glow=side==='left'?'#b45cff':'#45caff';
  const edge=side==='left'?'#d7a2ff':'#8be6ff';
  return <svg className={`dragon dragon-${side}`} viewBox="0 0 430 470" style={{transform:flip}} aria-hidden="true">
    <defs>
      <linearGradient id={`${id}-body`} x1="0" y1="0" x2="1" y2="1"><stop stopColor={side==='left'?'#8e3bd0':'#2b9ac5'}/><stop offset=".36" stopColor={side==='left'?'#35105f':'#0d4263'}/><stop offset="1" stopColor="#05040d"/></linearGradient>
      <linearGradient id={`${id}-wing`} x1="0" y1="0" x2="1" y2="1"><stop stopColor={side==='left'?'#c36cff':'#55d7ff'} stopOpacity=".72"/><stop offset=".7" stopColor={side==='left'?'#32105c':'#0b3a57'} stopOpacity=".30"/><stop offset="1" stopColor="#03030b" stopOpacity=".05"/></linearGradient>
      <filter id={`${id}-glow`}><feGaussianBlur stdDeviation="2.6" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    </defs>
    <g opacity=".28" fill="none" stroke={glow} strokeWidth="1">
      <path d="M55 390C10 278 70 128 202 77C314 34 409 95 414 205"/>
      <path d="M28 423C78 304 119 215 258 134C327 94 384 107 421 152"/>
      <ellipse cx="226" cy="241" rx="188" ry="119" transform="rotate(-19 226 241)"/>
    </g>
    <g filter={`url(#${id}-glow)`}>
      <path d="M93 442c-42-39-58-91-39-130 15-31 50-48 69-78 18-29 5-60 17-94 13-37 46-66 88-83-19 28-21 53-3 67 20 16 54 4 81 22 32 21 41 58 23 88-18 30-57 43-55 78 2 39 58 55 70 99 12 44-12 82-54 104-48 25-124 24-197-4z" fill={`url(#${id}-body)`} stroke={edge} strokeWidth="2.5"/>
      <path d="M169 113C123 72 89 54 45 48l46 52-34 48 77-21 39 25z" fill={`url(#${id}-wing)`} stroke={edge} strokeWidth="2.3"/>
      <path d="M242 124c47-45 93-69 144-77l-51 49 39 44-81-17-38 26z" fill={`url(#${id}-wing)`} stroke={edge} strokeWidth="2.3"/>
      <path d="M173 112c15-24 39-38 67-35 31 4 52 26 49 51-3 25-27 43-52 38-19-4-31-19-29-36 2-12 10-21 22-27" fill="none" stroke={edge} strokeWidth="4"/>
      <path d="M160 111 143 73 128 91 112 57 105 106M246 116l19-42 13 20 18-35 5 56" fill="none" stroke={edge} strokeWidth="3" strokeLinejoin="round"/>
      <path d="M247 127c17-10 31-9 42 2" fill="none" stroke={edge} strokeWidth="2"/>
      <circle cx="247" cy="126" r="6" fill="#fff" stroke={glow} strokeWidth="3"/>
      <circle cx="248" cy="126" r="1.8" fill="#16001f"/>
      <path d="M286 151c27 9 46 23 61 44M286 160c31 18 51 36 65 61M283 173c29 25 47 48 58 72" fill="none" stroke={edge} strokeWidth="1.4" opacity=".72"/>
      <path d="M105 191c51 31 104 34 155 9M91 230c59 34 116 37 174 10M83 271c60 31 123 37 185 10M85 314c57 27 117 32 177 9M101 356c48 22 98 25 149 8M123 396c38 15 78 17 117 7" fill="none" stroke={glow} strokeWidth="2" opacity=".58"/>
      <path d="M115 182l-25 26 37-8M146 176l-20 34 37-17M180 169l-12 39 31-28M215 166l-3 41 27-35M250 168l9 38 20-30" fill="none" stroke={edge} strokeWidth="1.8" opacity=".7"/>
      <path d="M69 399c47 26 109 35 177 12 31-10 58-26 79-49" fill="none" stroke={edge} strokeWidth="5" opacity=".24"/>
      <path d="M57 49l-25-13M79 76 42 88M351 50l27-17M365 78l38 12" stroke={edge} strokeWidth="2" opacity=".55"/>
    </g>
  </svg>
}

export function Crystal({large=false}:{large?:boolean}){
  return <div className={`crystal-stage ${large?'crystal-stage-large':''}`}>
    <div className="magic-stars"/><div className="orbit orbit-a"/><div className="orbit orbit-b"/><div className="orbit orbit-c"/>
    <div className="rune-ring rune-ring-a">✦ · ◇ · ✧ · ◇ · ✦ · ◇ · ✧</div><div className="rune-ring rune-ring-b">ᛉ · ✧ · ᛟ · ✦ · ᛉ · ✧</div>
    <motion.div className="crystal-aura" animate={{scale:[.9,1.08,.9],opacity:[.3,.78,.3]}} transition={{duration:4.5,repeat:Infinity,ease:'easeInOut'}}/>
    <motion.div className="crystal-core" animate={{y:[0,-8,0],rotateY:[0,180,360]}} transition={{duration:8,repeat:Infinity,ease:'easeInOut'}}>
      <div className="crystal-face crystal-front"><span>✦</span><i/><b/><em/><u/></div>
      <div className="crystal-face crystal-back"><span>◆</span><i/><b/><em/><u/></div>
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
