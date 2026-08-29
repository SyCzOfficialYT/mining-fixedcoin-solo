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
  return <><span className="corner corner-tl" /><span className="corner corner-tr" /><span className="corner corner-bl" /><span className="corner corner-br" /><span className="panel-rune rune-a">✧</span><span className="panel-rune rune-b">◇</span></>;
}

export function Dragon({ side }: { side: 'left' | 'right' }) {
  const id = `dragon-${side}`;
  return (
    <svg className={`dragon dragon-${side}`} viewBox="0 0 420 520" aria-hidden="true">
      <defs>
        <linearGradient id={`${id}-body`} x1="0" y1="0" x2="1" y2="1">
          <stop stopColor={side === 'left' ? '#d29aff' : '#77dcff'} />
          <stop offset=".28" stopColor={side === 'left' ? '#7b2bc5' : '#2377a9'} />
          <stop offset=".72" stopColor="#211044" />
          <stop offset="1" stopColor="#05040b" />
        </linearGradient>
        <linearGradient id={`${id}-wing`} x1="0" y1="0" x2="1" y2="1">
          <stop stopColor={side === 'left' ? '#8d49df' : '#368fc1'} stopOpacity=".9" />
          <stop offset="1" stopColor="#080612" stopOpacity=".1" />
        </linearGradient>
        <radialGradient id={`${id}-eye`}><stop stopColor="#fff"/><stop offset=".25" stopColor={side === 'left' ? '#e2a4ff' : '#9eeaff'}/><stop offset="1" stopColor={side === 'left' ? '#9b3fff' : '#32cfff'}/></radialGradient>
        <filter id={`${id}-glow`}><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      </defs>
      <g transform={side === 'right' ? 'translate(420 0) scale(-1 1)' : undefined}>
        <path d="M274 503c-70-16-113-62-107-123 4-38 34-65 31-99-3-37-44-52-45-98-1-53 36-95 99-119-30 31-34 61-14 81 22 22 66 14 88 39 28 31 9 68-9 94-15 22-20 43-6 64 16 24 59 40 63 83 4 38-21 67-58 78l-17-18c20-19 24-40 10-57-19-23-55-28-65-60-11-35 13-63 10-92-4-30-27-44-28-74 12 37 39 55 63 56 27 2 50-13 67 8 20 25-3 56-4 82-1 36 34 55 43 92 13 53-27 93-78 113-34 14-72 17-121 19z" fill={`url(#${id}-body)`} stroke={side === 'left' ? '#bb73ff' : '#65d8ff'} strokeWidth="2.5" filter={`url(#${id}-glow)`}/>
        <path d="M217 155 73 45l93 34L203 4l17 119 66-78 35 38 79-13-111 92" fill={`url(#${id}-wing)`} stroke={side === 'left' ? '#a963f5' : '#54c8f0'} strokeWidth="3" opacity=".88"/>
        <path d="M215 158 90 64l75 30 31-49 15 84M252 167l93-89-60 31-24-48" fill="none" stroke="#e3c7ff" strokeWidth="1.6" opacity=".5"/>
        <path d="M254 113c32-21 61-18 78 4 10 13 8 31-6 42-18 14-40 10-58-2l-19-13 18-31z" fill={`url(#${id}-body)`} stroke={side === 'left' ? '#b870ff' : '#5ad7ff'} strokeWidth="2"/>
        <path d="M315 102l25-16-12 25 26 7-31 6-18 18" fill="none" stroke="#e8d5ff" strokeWidth="2" opacity=".75"/>
        <ellipse cx="311" cy="126" rx="5" ry="4" fill={`url(#${id}-eye)`} filter={`url(#${id}-glow)`}/>
        <path d="M331 143l24 4-24 6M321 149l22 14-28-6M305 148l11 22-20-15" fill="none" stroke={side === 'left' ? '#c887ff' : '#69dcff'} strokeWidth="2"/>
        <path d="M202 208c39 23 74 22 111 3M184 242c48 28 91 25 129 1M177 279c44 25 84 24 122 5M182 316c40 23 75 23 109 8M194 352c32 18 61 19 89 10" fill="none" stroke={side === 'left' ? '#9b54d4' : '#358bb5'} strokeWidth="3" opacity=".5"/>
        <g fill="none" stroke={side === 'left' ? '#c58aff' : '#69dfff'} strokeWidth="1.5" opacity=".65">
          <path d="M205 215l18-9 15 10-14 11zM238 226l19-8 15 10-16 12zM198 250l19-8 16 11-16 12zM230 265l20-9 15 12-17 12z"/>
          <path d="M193 291l19-8 15 10-15 12zM225 307l20-9 15 11-16 12zM202 333l19-8 15 10-15 12z"/>
        </g>
        <path d="M198 392c25 18 55 23 84 15M188 423c31 17 66 18 98 5M179 454c34 13 68 11 96-2" fill="none" stroke={side === 'left' ? '#7d3cb6' : '#2b7095'} strokeWidth="2" opacity=".7"/>
        <path d="M279 180l-7 34 18-14 5 25 16-21 7 23 13-25 7 18" fill="none" stroke="#f0dcff" strokeWidth="2" opacity=".55"/>
      </g>
    </svg>
  );
}

export function Crystal({ large = false }: { large?: boolean }) {
  return (
    <div className={`crystal-stage ${large ? 'crystal-stage-large' : ''}`}>
      <div className="magic-stars" />
      <div className="rune-ring rune-ring-1">✦</div><div className="rune-ring rune-ring-2">◇</div>
      <div className="orbit orbit-a" /><div className="orbit orbit-b" /><div className="orbit orbit-c" />
      <motion.div className="crystal-aura" animate={{ scale: [0.9, 1.12, 0.9], opacity: [0.32, 0.75, 0.32] }} transition={{ duration: 4.5, repeat: Infinity, ease: 'easeInOut' }} />
      <motion.svg className="crystal-svg" viewBox="0 0 180 300" animate={{ y: [0, -8, 0], rotate: [0, 1.5, 0, -1.5, 0] }} transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }} aria-hidden="true">
        <defs>
          <linearGradient id="crystal-main" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#fff0ff"/><stop offset=".18" stopColor="#d49aff"/><stop offset=".42" stopColor="#8a3fe5"/><stop offset=".74" stopColor="#48139a"/><stop offset="1" stopColor="#100522"/></linearGradient>
          <linearGradient id="crystal-side" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#82efff"/><stop offset=".4" stopColor="#4e78ff"/><stop offset="1" stopColor="#26105c"/></linearGradient>
          <filter id="crystal-glow"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        <path d="M90 8 142 49 166 149 132 257 90 292 48 257 14 149 38 49z" fill="url(#crystal-main)" stroke="#d6a3ff" strokeWidth="2" filter="url(#crystal-glow)"/>
        <path d="M90 8v284M38 49l52 49 52-49M14 149l76-51 76 51M48 257l42-159 42 159" fill="none" stroke="#f4dcff" strokeWidth="1.5" opacity=".45"/>
        <path d="M90 8 38 49l52 49zM90 98l-76 51 76 41zM90 98l76 51-76 41z" fill="rgba(255,255,255,.15)"/>
        <path d="M90 98 142 49l24 100-76 41z" fill="url(#crystal-side)" opacity=".62"/>
        <path d="M90 98 48 257l42 35z" fill="#6c2fbd" opacity=".5"/>
        <path d="M48 257 90 292 132 257 90 239z" fill="#32106c" opacity=".8"/>
        <path d="M61 73 90 49l29 24-29 25z" fill="#fff" opacity=".16"/>
        <text x="90" y="174" textAnchor="middle" fill="#fff" fontSize="25" fontFamily="Georgia" opacity=".9">✦</text>
      </motion.svg>
      <div className="crystal-pedestal"><span /><i /><b /><em /></div>
    </div>
  );
}

export function ScaleArt() {
  return <svg className="scale-art" viewBox="0 0 420 300" aria-hidden="true">
    <defs><linearGradient id="gold-scale" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#fff2a8"/><stop offset=".35" stopColor="#e5b84e"/><stop offset=".7" stopColor="#9d6519"/><stop offset="1" stopColor="#4a2a08"/></linearGradient><radialGradient id="coin-glow"><stop stopColor="#f5d76e" stopOpacity=".8"/><stop offset="1" stopColor="#f5d76e" stopOpacity="0"/></radialGradient></defs>
    <ellipse cx="210" cy="267" rx="150" ry="24" fill="url(#coin-glow)" opacity=".35"/>
    <g fill="none" stroke="url(#gold-scale)" strokeLinecap="round" strokeLinejoin="round">
      <path d="M210 36v207M165 243h90M145 262h130" strokeWidth="7"/><circle cx="210" cy="39" r="15" fill="#0c0914" strokeWidth="3"/>
      <path d="M72 94h276M98 94 48 183q50 34 100 0L98 94M322 94l50 89q-50 34-100 0l100-89" strokeWidth="5"/>
      <path d="M53 183h91M276 183h91" strokeWidth="3" opacity=".7"/><circle cx="98" cy="94" r="6" fill="#ffe98e"/><circle cx="322" cy="94" r="6" fill="#ffe98e"/>
      <path d="M210 57l-20 20 20 20 20-20z" strokeWidth="2"/><path d="M190 77h40" strokeWidth="2"/>
    </g>
    <g fill="#e6b94f" opacity=".8"><circle cx="75" cy="230" r="4"/><circle cx="96" cy="246" r="3"/><circle cx="333" cy="235" r="4"/><circle cx="315" cy="251" r="3"/><circle cx="205" cy="256" r="4"/></g>
  </svg>;
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
  return <div className="brand-mark"><div className="brand-crest"><span>✧</span></div><span>FIXEDCOIN<small>SOLO NODE</small></span></div>;
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
