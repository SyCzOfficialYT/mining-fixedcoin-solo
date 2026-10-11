'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { Activity, ArrowDownRight, ArrowUpRight, Blocks, CheckCircle2, CircleAlert, Clock3, Database, Gauge, Layers3, Radio, RefreshCw, Search, Waves } from 'lucide-react';

type Tx = { txid:string; size:number; vsize:number; weight:number; fee:number; fee_rate:number; time:number; height:number; ancestor_count:number; descendant_count:number };
type Payload = { status?:string; ts?:number; mempool?:{loaded?:boolean;size?:number;bytes?:number;usage?:number;total_fee?:number;min_fee?:number;relay_fee?:number;transactions?:number;fee_rate_min?:number;fee_rate_median?:number;fee_rate_max?:number}; transactions?:Tx[]; error?:string; details?:string };
const n=(v:unknown)=>Number.isFinite(Number(v))?Number(v):0;
const compact=(v:number)=>new Intl.NumberFormat('en-US',{notation:'compact',maximumFractionDigits:2}).format(v);
const bytes=(v:number)=>v>=1e6?(v/1e6).toFixed(2)+' MB':v>=1e3?(v/1e3).toFixed(1)+' KB':v+' B';
const coin=(v:number)=>v.toFixed(8)+' FIX';
const age=(v:number)=>{if(!v)return '—';const sec=Math.max(0,Math.floor(Date.now()/1000-v));return sec<60?sec+'s ago':sec<3600?Math.floor(sec/60)+'m ago':Math.floor(sec/3600)+'h ago'};
const short=(s:string)=>s.length>20?s.slice(0,10)+'…'+s.slice(-7):s;

export default function MempoolPage(){
 const [data,setData]=useState<Payload>({});
 const [loading,setLoading]=useState(true);
 const [error,setError]=useState('');
 const [query,setQuery]=useState('');
 const [sort,setSort]=useState<'fee_rate'|'time'|'vsize'>('fee_rate');
 const [updated,setUpdated]=useState(0);
 async function refresh(){try{const r=await fetch('/api/mempool?ts='+Date.now(),{cache:'no-store'});const j=await r.json();if(!r.ok)throw new Error(j.details||j.error||'Mempool RPC unavailable');setData(j);setError('');setUpdated(Date.now())}catch(e){setError(e instanceof Error?e.message:'Unable to load mempool')}finally{setLoading(false)}}
 useEffect(()=>{void refresh();const id=window.setInterval(()=>void refresh(),10000);return()=>window.clearInterval(id)},[]);
 const pool=data.mempool||{};
 const txs=useMemo(()=>{const q=query.trim().toLowerCase();return [...(data.transactions||[])].filter(t=>!q||t.txid.toLowerCase().includes(q)).sort((a,b)=>n(b[sort])-n(a[sort]))},[data.transactions,query,sort]);
 const bins=useMemo(()=>{const counts=Array(12).fill(0) as number[];for(const tx of data.transactions||[]){const rate=Math.max(0,n(tx.fee_rate));const index=Math.min(11,Math.floor(Math.log10(rate+1)*2));counts[index]++}return counts},[data.transactions]);
 const maxBin=Math.max(1,...bins);
 return <main className="mempool-shell">
  <aside className="mp-sidebar">
   <Link href="/" className="mp-brand"><span className="mp-brand-icon"><Layers3 size={21}/></span><span>FIXEDCOIN<small>NETWORK EXPLORER</small></span></Link>
   <div className="mp-nav-label">EXPLORER</div>
   <Link href="/" className="mp-nav"><Activity size={17}/> Overview</Link>
   <Link href="/mempool" className="mp-nav active"><Waves size={17}/> Mempool <i/></Link>
   <Link href="/#blockHistory" className="mp-nav"><Blocks size={17}/> Blocks</Link>
   <div className="mp-sidebar-bottom"><span className={error?'mp-dot bad':'mp-dot'}/><span>{error?'NODE UNAVAILABLE':'NODE LINK'}</span><small>FIX RPC · PRIVATE</small></div>
  </aside>
  <section className="mp-main">
   <header className="mp-topbar"><div><span className="mp-crumb">NETWORK /</span> MEMPOOL EXPLORER</div><div className="mp-top-actions"><span className={error?'mp-status offline':'mp-status'}><i/>{error?'DEGRADED':'LIVE DATA'}</span><button className="mp-refresh" onClick={()=>void refresh()} aria-label="Refresh mempool"><RefreshCw size={15}/><span>Refresh</span></button></div></header>
   <div className="mp-heading"><div><div className="mp-kicker"><span/> FIXEDCOIN CORE · TRANSACTION LAYER</div><h1>Mempool <em>Explorer</em></h1><p>Unconfirmed transactions, fee pressure and network activity — directly from your FixedCoin node.</p></div><div className="mp-block-pill"><Radio size={15}/><span><b>{pool.loaded===false?'LOADING':'LIVE NODE'}</b><small>{updated?'Updated '+new Date(updated).toLocaleTimeString():'Waiting for first response'}</small></span></div></div>
   {error&&<div className="mp-error"><CircleAlert size={18}/><div><b>Could not load live mempool data</b><p>{error}. Verify that FixedCoin Core is running and supports getmempoolinfo/getrawmempool.</p></div><button onClick={()=>void refresh()}>Retry</button></div>}
   <div className="mp-stats">
    <article className="mp-stat"><div className="mp-stat-top"><span>UNCONFIRMED TX</span><Database size={17}/></div><strong>{loading?'—':compact(n(pool.transactions))}</strong><small><span className="mp-accent">{n(pool.transactions).toLocaleString()}</span> transactions in node mempool</small><div className="mp-stat-line"><i style={{width:Math.min(100,n(pool.transactions)/Math.max(1,n(pool.transactions))*100)+'%'}}/></div></article>
    <article className="mp-stat"><div className="mp-stat-top"><span>MEMPOOL SIZE</span><Layers3 size={17}/></div><strong>{loading?'—':bytes(n(pool.bytes))}</strong><small>{bytes(n(pool.usage))} allocated memory usage</small><div className="mp-stat-line cyan"><i style={{width:Math.min(100,n(pool.usage)/Math.max(1,n(pool.bytes))*100)+'%'}}/></div></article>
    <article className="mp-stat"><div className="mp-stat-top"><span>MEDIAN FEE RATE</span><Gauge size={17}/></div><strong>{loading?'—':n(pool.fee_rate_median).toFixed(2)} <small className="mp-unit">sat/vB*</small></strong><small>Min {n(pool.fee_rate_min).toFixed(2)} · Max {n(pool.fee_rate_max).toFixed(2)}</small><div className="mp-stat-line lime"><i style={{width:Math.min(100,n(pool.fee_rate_median)/Math.max(1,n(pool.fee_rate_max))*100)+'%'}}/></div></article>
    <article className="mp-stat"><div className="mp-stat-top"><span>TOTAL MEMPOOL FEES</span><ArrowUpRight size={17}/></div><strong>{loading?'—':coin(n(pool.total_fee))}</strong><small>Reported by FixedCoin Core</small><div className="mp-stat-line violet"><i style={{width:pool.transactions?100:0+'%'}}/></div></article>
   </div>
   <div className="mp-content-grid">
    <section className="mp-panel mp-fees"><div className="mp-panel-head"><div><span className="mp-section-kicker">FEE MARKET</span><h2>Fee-rate distribution</h2></div><span className="mp-live-mini"><i/> LIVE</span></div><p className="mp-panel-desc">Transactions grouped by a logarithmic fee-rate band. Select a transaction below to inspect its reported fee details.</p><div className="mp-chart" role="img" aria-label="Mempool fee rate distribution histogram">{bins.map((v,i)=><div className="mp-bar-wrap" key={i}><div className="mp-bar-count">{v||''}</div><div className="mp-bar" style={{height:Math.max(4,v/maxBin*100)+'%'}}/><span>{i===0?'<1':i===11?'100+':(Math.pow(10,i/2)-1).toFixed(0)}</span></div>)}</div><div className="mp-chart-legend"><span><i/> Transactions per fee band</span><span>Logarithmic scale</span></div><div className="mp-fee-summary"><div><small>MIN RELAY FEE</small><b>{n(pool.relay_fee).toFixed(8)} FIX/kB</b></div><div><small>MEMPOOL MIN FEE</small><b>{n(pool.min_fee).toFixed(8)} FIX/kB</b></div></div><small className="mp-footnote">* Fee rate is derived from RPC fee values and virtual size. Confirm unit conventions for your FixedCoin Core build before using it as a mining-fee quote.</small></section>
    <section className="mp-panel mp-health"><div className="mp-panel-head"><div><span className="mp-section-kicker">NODE TELEMETRY</span><h2>Mempool health</h2></div><Activity size={18}/></div><div className="mp-health-row"><span>RPC connection</span><b className={error?'bad':'good'}>{error?'Unavailable':'Connected'}</b></div><div className="mp-health-row"><span>Loaded state</span><b>{pool.loaded===false?'Loading':data.status==='online'?'Ready':'—'}</b></div><div className="mp-health-row"><span>Transactions indexed</span><b>{n(data.transactions?.length).toLocaleString()}</b></div><div className="mp-health-row"><span>Refresh interval</span><b>10 seconds</b></div><div className="mp-health-callout"><CheckCircle2 size={17}/><p>RPC credentials remain server-side. This page only receives normalized mempool telemetry.</p></div><div className="mp-health-links"><Link href="/">← Dashboard overview</Link><span>FIXEDCOIN / SOLO</span></div></section>
   </div>
   <section className="mp-panel mp-transactions"><div className="mp-panel-head mp-transactions-head"><div><span className="mp-section-kicker">TRANSACTION QUEUE</span><h2>Unconfirmed transactions <span className="mp-count">{n(pool.transactions).toLocaleString()}</span></h2></div><div className="mp-table-tools"><label className="mp-search"><Search size={15}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search TXID…"/></label><select value={sort} onChange={e=>setSort(e.target.value as typeof sort)} aria-label="Sort transactions"><option value="fee_rate">Highest fee rate</option><option value="time">Newest first</option><option value="vsize">Largest virtual size</option></select></div></div>
    <div className="mp-table-wrap"><table className="mp-table"><thead><tr><th>TRANSACTION ID</th><th>FEE RATE*</th><th>FEE</th><th>VIRTUAL SIZE</th><th>AGE</th><th>ANCESTORS</th></tr></thead><tbody>{txs.slice(0,100).map(tx=><tr key={tx.txid}><td><code title={tx.txid}>{short(tx.txid)}</code><button className="mp-copy" onClick={()=>navigator.clipboard?.writeText(tx.txid)} aria-label="Copy transaction ID">Copy</button></td><td><b className="mp-fee-rate">{n(tx.fee_rate).toFixed(2)}</b><small>sat/vB*</small></td><td>{coin(n(tx.fee))}</td><td>{n(tx.vsize).toLocaleString()} vB</td><td>{age(tx.time)}</td><td>{n(tx.ancestor_count)||'—'}</td></tr>)}</tbody></table>{!txs.length&&<div className="mp-empty">{loading?'Loading mempool transactions…':query?'No transaction matches your search.':'The mempool is empty or no transaction data is available.'}</div>}</div><footer className="mp-table-footer"><span>Showing {Math.min(100,txs.length)} of {txs.length.toLocaleString()} matching transactions</span><span><span className="mp-dot"/> Data from your own FixedCoin node</span></footer>
   </section>
   <footer className="mp-footer"><span>FIXEDCOIN NETWORK EXPLORER</span><span>NOT FINANCIAL ADVICE · RPC-DERIVED DATA</span></footer>
  </section>
 </main>
}
