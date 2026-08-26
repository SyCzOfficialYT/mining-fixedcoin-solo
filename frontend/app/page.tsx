'use client';

import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';

type Status={node?:any;mining?:any;round?:any;wallet?:any;blocks?:any[];competition?:any;ts?:number};
const n=(v:any)=>Number(v)||0;
const compact=(v:any)=>{const x=n(v);if(x>=1e9)return(x/1e9).toFixed(2)+'B';if(x>=1e6)return(x/1e6).toFixed(2)+'M';if(x>=1e3)return(x/1e3).toFixed(2)+'K';return x.toFixed(x<10?2:0)};
const hash=(v:any)=>{const x=n(v);if(x>=1e12)return(x/1e12).toFixed(2)+' TH/s';if(x>=1e9)return(x/1e9).toFixed(2)+' GH/s';if(x>=1e6)return(x/1e6).toFixed(2)+' MH/s';if(x>=1e3)return(x/1e3).toFixed(2)+' KH/s';return x.toFixed(1)+' H/s'};
const coins=(v:any)=>n(v).toFixed(8)+' FIX';
const eta=(diff:any,hr:any)=>{const seconds=n(diff)*4294967296/n(hr);if(!seconds||!Number.isFinite(seconds))return '—';const d=Math.floor(seconds/86400),h=Math.floor(seconds%86400/3600),m=Math.floor(seconds%3600/60);return d?`~${d}d ${h}h`:h?`~${h}h ${m}m`:`~${m}m`};

export default function Home(){
 const [s,setS]=useState<Status>({}); const [error,setError]=useState(false); const [last,setLast]=useState(0);
 useEffect(()=>{let alive=true;const load=async()=>{try{const r=await fetch('/api/status?ts='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error();const x=await r.json();if(alive){setS(x);setError(false);setLast(Date.now())}}catch{if(alive)setError(true)}};load();const id=setInterval(load,2000);return()=>{alive=false;clearInterval(id)}},[]);
 const m=s.mining||{},r=s.round||{},node=s.node||{},w=s.wallet||{}, blocks=s.blocks||[]; const best=n(r.best_share||m.best_share), network=n(r.difficulty||node.difficulty), progress=Math.min(100,network?best/network*100:0), accepted=n(m.accepted), rejected=n(m.rejected), total=accepted+rejected;
 const recent=Array.isArray(s.blocks)?blocks.slice(0,8):[];
 return <main className="app">
  <div className="topbar"><div className="brand">LIVESHARE <span>✦</span> ARCANE FORGE</div><div className="live"><i className="dot"/> {error?'API DEGRADED':'STRATUM · LIVE'}</div></div>
  <section className="grid hero">
   <div className="panel heroMain"><div className="eyebrow">ARCANE SOLO MINING NETWORK</div><h1>Forge your next block.</h1><p className="sub">Real-time FixedCoin proof-of-work command center · cyber mythic edition.</p>
    <div className="heroStats"><div className="metric"><label>BEST SHARE DIFFICULTY</label><strong>{compact(best)}</strong></div><div className="vs">VS</div><div className="metric network"><label>NETWORK BLOCK TARGET</label><strong>{compact(network)}</strong></div></div>
    <div className="track"><motion.i animate={{width:`${progress}%`}} transition={{duration:.7}}/></div><div className="trackRow"><span>0</span><b>{progress.toFixed(3)}%</b><span>100% · BLOCK TARGET</span></div>
   </div>
   <aside className="panel round"><div className="eyebrow">CURRENT ROUND</div><strong>#{n(r.height||node.height).toLocaleString()}</strong><div className="mini"><label>ROUND TARGET</label><b>10:00</b></div><div className="mini" style={{marginTop:18}}><label>NETWORK DIFFICULTY</label><b>{compact(network)}</b></div><span className="status">{node.online?'ACTIVE':'DEGRADED'}</span></aside>
  </section>
  <section className="panel forge"><div className="forgeHead"><div className="eyebrow">LIVE SHARE FORGE · REALTIME PROOF OF WORK</div><div className="live"><i className="dot"/> {hash(m.hashrate_5m)}</div></div>
   <div className="forgeStage">
    <div className="side"><div className="card"><label>HASHRATE</label><strong>{hash(m.hashrate_5m)}</strong><div className="spark"/></div><div className="card"><label>SHARES / MIN</label><strong>{n(m.round_shares).toFixed(1)}</strong><div className="spark"/></div></div>
    <div className="coreWrap"><div className="coreGlow"/><div className="core"><div className="ring"/><div className="ring"/><div className="ring"/><motion.div className="crystal" animate={{scale:[1,1.05,1],rotateY:[0,180,360]}} transition={{duration:8,repeat:Infinity,ease:'easeInOut'}}/></div><div className="coreTitle">LIVESHARE <span>· ARCANE CORE</span></div><div className="coreSub">MAGIC ENERGY // LIVE HASH STREAM // SHA256</div></div>
    <div className="side"><div className="card counter"><label>ACCEPTED SHARES</label><strong>{accepted.toLocaleString()}</strong><div className="spark"/></div><div className="card counter reject"><label>REJECTED SHARES</label><strong>{rejected.toLocaleString()}</strong><div className="spark"/></div></div>
   </div>
  </section>
  <section className="grid lower">
   <div className="panel candidate"><div className="heading"><div className="sigil">✦</div><div><h2>BLOCK CANDIDATE · ARCANE PROXIMITY</h2><p>Best submitted work measured against the current network target.</p></div></div><motion.div className="candidateValue" animate={{textShadow:[`0 0 20px rgba(165,108,255,.2)`,`0 0 42px rgba(165,108,255,.6)`,`0 0 20px rgba(165,108,255,.2)`]}} transition={{duration:2.5,repeat:Infinity}}>{progress.toFixed(3)}%</motion.div><div className="track"><motion.i animate={{width:`${progress}%`}} transition={{duration:.7}}/></div><div className="trackRow"><span>PROGRESS TO BLOCK</span><span>NEXT #{(n(r.height||node.height)+1).toLocaleString()}</span></div></div>
   <div className="panel balance"><div className="heading"><div className="sigil">◈</div><div><h2>ARCANE TREASURY</h2><p>Wallet state · live chain economy</p></div></div><div className="balanceGrid"><div className="balanceItem"><label>CONFIRMED</label><strong className="green">{coins(w.confirmed)}</strong></div><div className="balanceItem"><label>PENDING</label><strong>{coins(w.pending)}</strong></div><div className="balanceItem"><label>IMMATURE</label><strong>{coins(w.immature)}</strong></div><div className="balanceItem"><label>TOTAL</label><strong>{coins(w.total)}</strong></div></div></div>
  </section>
  <section className="panel history"><div className="heading"><div className="sigil">◆</div><div><h2>CHRONICLES OF THE FIXEDCOIN CHAIN</h2><p>Validated blocks · confirmations · rewards</p></div></div><div className="table"><div className="row head"><span>HEIGHT</span><span>VALIDITY</span><span>CONFIRMATIONS</span><span>REWARD</span><span>BLOCK HASH</span></div>{recent.length?recent.map((b:any,i:number)=><div className="row" key={`${b.height}-${i}`}><span>#{n(b.height).toLocaleString()}</span><span><b className="pill">{String(b.state||'IMMATURE')}</b></span><span>{n(b.confirmations)} / {n(b.validity_target||100)}</span><span className="gold">{n(b.reward).toFixed(4)}</span><span title={b.blockhash||b.txid}>{String(b.blockhash||b.txid||'—').slice(0,28)}…</span></div>):<div className="row"><span>Waiting for blocks…</span></div>}</div></section>
  <footer className="footer"><strong>LIVESHARE · FIXEDCOIN SOLO</strong><span>PEERS <b>{n(node.connections)}</b></span><span>NETWORK <b>{compact(network)}</b></span><span>ETA <b>{eta(network,n(m.hashrate_5m))}</b></span><span>SYNC <b>{node.synced?'YES':'CHECKING'}</b></span><span>REFRESH <b>{last?new Date(last).toLocaleTimeString():'—'}</b></span></footer>
 </main>
}
