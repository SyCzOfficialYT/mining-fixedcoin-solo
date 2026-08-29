'use client';

import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';
import {
  Activity, Blocks, CircleDollarSign, Cpu, Gauge, Gem, Hammer, History,
  LayoutDashboard, Network, Settings, ShieldCheck, Sparkles, Users, Wallet,
} from 'lucide-react';

export const navItems: ReadonlyArray<readonly [string, LucideIcon]> = [
  ['Dashboard', LayoutDashboard], ['Mining', Hammer], ['Shares', Activity],
  ['Blocks', Blocks], ['Workers', Users], ['Settings', Settings], ['Logs', History], ['System', Network],
];

export function OrnateCorners() {
  return <><span className="corner corner-tl" /><span className="corner corner-tr" /><span className="corner corner-bl" /><span className="corner corner-br" /></>;
}

export function Dragon({ side }: { side: 'left' | 'right' }) {
  const flip = side === 'right' ? 'scaleX(-1)' : undefined;
  return (
    <svg className={`dragon dragon-${side}`} viewBox="0 0 340 500" style={{ transform: flip }} aria-hidden="true">
      <defs>
        <linearGradient id={`dragon-${side}`} x1="0" y1="0" x2="1" y2="1">
          <stop stopColor={side === 'left' ? '#b765ff' : '#63d8ff'} />
          <stop offset=".48" stopColor={side === 'left' ? '#42137b' : '#124c78'} />
          <stop offset="1" stopColor="#05040c" />
        </linearGradient>
        <filter id={`dragon-glow-${side}`}><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      </defs>
      <path filter={`url(#dragon-glow-${side})`} d="M174 488c-64-22-104-70-88-132 11-42 55-55 54-95-2-42-55-57-45-108 10-49 54-89 111-101-43 31-46 68-13 86 39 21 94-3 107 44 13 46-41 80-28 122 13 43 78 68 67 125-10 52-43 76-96 82l-16-23c28-16 37-42 19-62-23-27-70-27-83-66-12-38 20-69 13-101-8-34-39-46-40-81-1 41 27 65 53 72 33 9 59-8 76 17 17 26-5 55-7 81-3 42 38 72 25 114-10 32-39 43-69 25z" fill={`url(#dragon-${side})`} stroke={side === 'left' ? '#a967ff' : '#4cc9ff'} strokeWidth="2"/>
      <path d="M132 142 38 60l82 22 42-58 9 91M207 145l93-78-78 21-39-61-9 92" fill="none" stroke={side === 'left' ? '#c98bff' : '#74dcff'} strokeWidth="3" opacity=".72"/>
      <circle cx="211" cy="137" r="6" fill="#fff" />
      <path d="M100 352c48 30 100 31 151-7M89 397c52 29 106 27 158-7" fill="none" stroke={side === 'left' ? '#7f42bd' : '#237eaa'} strokeWidth="2" opacity=".45"/>
    </svg>
  );
}

export function Crystal({ large = false }: { large?: boolean }) {
  return (
    <div className={`crystal-stage ${large ? 'crystal-stage-large' : ''}`}>
      <div className="magic-stars" />
      <div className="orbit orbit-a" /><div className="orbit orbit-b" /><div className="orbit orbit-c" />
      <motion.div className="crystal-aura" animate={{ scale: [0.92, 1.08, 0.92], opacity: [0.35, 0.78, 0.35] }} transition={{ duration: 4.5, repeat: Infinity, ease: 'easeInOut' }} />
      <motion.div className="crystal-core" animate={{ y: [0, -8, 0], rotateY: [0, 180, 360] }} transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}>
        <div className="crystal-face crystal-front">✦</div><div className="crystal-face crystal-back">◆</div>
      </motion.div>
      <div className="crystal-pedestal"><span /><i /><b /></div>
    </div>
  );
}

export function ScaleArt() {
  return <svg className="scale-art" viewBox="0 0 340 260" aria-hidden="true"><defs><linearGradient id="gold-scale" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#fff1a3"/><stop offset=".45" stopColor="#d59a2f"/><stop offset="1" stopColor="#6a410e"/></linearGradient></defs><path d="M170 25v184M130 209h80M105 228h130" stroke="url(#gold-scale)" strokeWidth="7" strokeLinecap="round"/><circle cx="170" cy="29" r="14" fill="#100c17" stroke="#ffd96a" strokeWidth="3"/><path d="M53 77h234M78 77 41 151q37 28 74 0L78 77M262 77l37 74q-37 28-74 0l37-74" fill="none" stroke="#d7a43d" strokeWidth="5"/><circle cx="78" cy="77" r="5" fill="#ffe68b"/><circle cx="262" cy="77" r="5" fill="#ffe68b"/></svg>;
}

export function Panel({ title, subtitle, children, className = '', icon: Icon = Sparkles }: { title: string; subtitle?: string; children: ReactNode; className?: string; icon?: LucideIcon }) {
  return <section className={`magic-panel ${className}`}><OrnateCorners/><div className="panel-heading"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div><Icon size={16}/></div>{children}</section>;
}

export function MetricCard({ label, value, note, tone = 'violet', icon: Icon = Gauge }: { label: string; value: string; note?: string; tone?: string; icon?: LucideIcon }) {
  return <div className={`metric-card tone-${tone}`}><div className="metric-icon"><Icon size={15}/></div><span>{label}</span><strong>{value}</strong>{note && <small>{note}</small>}<div className="sparkline"><i/><i/><i/><i/><i/><i/><i/><i/></div></div>;
}

export function SideStat({ label, value, note, tone = 'violet', icon: Icon = Activity }: { label: string; value: string; note?: string; tone?: string; icon?: LucideIcon }) {
  return <div className={`side-stat tone-${tone}`}><div className="side-stat-icon"><Icon size={15}/></div><span>{label}</span><strong>{value}</strong><small>{note || 'LIVE TELEMETRY'}</small></div>;
}

export function ProgressLine({ value, tone = 'violet' }: { value: number; tone?: string }) {
  return <div className={`magic-progress tone-${tone}`}><i style={{ width: `${Math.max(0, Math.min(100, value))}%` }}/></div>;
}

export function LiveBadge({ degraded = false }: { degraded?: boolean }) {
  return <span className={`live-badge ${degraded ? 'degraded' : ''}`}><i/>{degraded ? 'API DEGRADED' : 'STRATUM · LIVE'}</span>;
}

export function BrandMark() {
  return <div className="brand-mark"><Gem size={22}/><span>FIXEDCOIN<small>SOLO NODE</small></span></div>;
}

export function StatusPill({ children }: { children: ReactNode }) {
  return <span className="badge badge-success badge-outline status-pill"><ShieldCheck size={13}/>{children}</span>;
}

export function DataIcon({ kind }: { kind: 'wallet'|'cpu'|'network'|'blocks' }) {
  const map = { wallet: Wallet, cpu: Cpu, network: Network, blocks: Blocks } as const;
  const Icon = map[kind];
  return <Icon size={15}/>;
}

export function DollarIcon() { return <CircleDollarSign size={15}/>; }
