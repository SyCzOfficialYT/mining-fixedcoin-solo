"use client";

import { useEffect, useMemo, useState } from "react";

type Share = { ts?: string; num?: number; work?: number; pool_diff?: number; hash?: string; worker?: string };
type Block = { height?: number; time?: number; difficulty?: number; luck?: number; shares?: number; miner?: string; hash?: string; reward?: number; blockhash?: string };
type Status = {
  status?: string; ts?: number;
  node?: { online?: boolean; synced?: boolean; height?: number; headers?: number; difficulty?: number; network_hashrate?: number; connections?: number };
  mining?: { accepted?: number; rejected?: number; reject_pct?: number; hashrate_5m?: number; hashrate_1h?: number; best_share?: number; best_share_pct?: number; difficulty_remaining?: number; round_work?: number; round_shares?: number; round_effort?: number; worker_count?: number };
  round?: { height?: number; shares?: number; work?: number; best_share?: number; effort_pct?: number; best_share_pct?: number; difficulty?: number; remaining?: number; started_at?: string; target_seconds?: number };
  competition?: { network_hashrate?: number };
  wallet?: { confirmed?: number; pending?: number; immature?: number; total?: number; total_rewards?: number };
  job?: { job_id?: string; height?: number; network_diff?: number };
  shares?: Share[]; blocks?: Block[];
};

const nf = new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 });
const n3 = new Intl.NumberFormat("en-US", { maximumFractionDigits: 3 });

function fmt(v: unknown, digits = 2) {
  const n = Number(v);
  if (!Number.isFinite(n)) return "—";
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(n);
}
function diff(v: unknown) {
  const n = Number(v);
  if (!Number.isFinite(n)) return "—";
  if (n >= 1e9) return `${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(2)}K`;
  return fmt(n);
}
function hash(v: unknown) {
  const n = Number(v);
  if (!Number.isFinite(n) || n <= 0) return "—";
  if (n >= 1e12) return `${(n / 1e12).toFixed(2)} TH/s`;
  if (n >= 1e9) return `${(n / 1e9).toFixed(2)} GH/s`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(2)} MH/s`;
  return `${(n / 1e3).toFixed(2)} KH/s`;
}
function timeAgo(ts?: string) {
  if (!ts) return "—";
  const t = Date.parse(ts.replace(" ", "T") + "Z");
  if (!Number.isFinite(t)) return ts.slice(11, 19);
  const s = Math.max(0, Math.floor((Date.now() - t) / 1000));
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  return `${Math.floor(s / 3600)}h ago`;
}
function short(v?: string, size = 12) {
  if (!v) return "—";
  return v.length > size ? `${v.slice(0, size)}…` : v;
}

function Crystal({ small = false }: { small?: boolean }) {
  return <div className={`crystal ${small ? "crystalSmall" : ""}`}><span>FX</span></div>;
}
function Dragon({ side }: { side: "left" | "right" }) {
  return <div className={`dragonArt dragon-${side}`} aria-hidden="true">
    <div className="dragonHalo" />
    <div className="dragonHead">{side === "left" ? "◈" : "◇"}</div>
    <div className="dragonBody" />
    <div className="dragonWing wingA" /><div className="dragonWing wingB" />
    <div className="dragonEye" />
  </div>;
}

export default function Home() {
  const [data, setData] = useState<Status>({});
  const [error, setError] = useState(false);
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const r = await fetch("/api/status", { cache: "no-store" });
        if (!r.ok) throw new Error("status");
        const next = await r.json();
        if (alive) { setData(next); setError(false); }
      } catch { if (alive) setError(true); }
    };
    load();
    const poll = window.setInterval(load, 2000);
    const clock = window.setInterval(() => setNow(Date.now()), 1000);
    return () => { alive = false; window.clearInterval(poll); window.clearInterval(clock); };
  }, []);

  const round = data.round ?? {};
  const mining = data.mining ?? {};
  const node = data.node ?? {};
  const wallet = data.wallet ?? {};
  const networkDiff = Number(round.difficulty || node.difficulty || data.job?.network_diff || 0);
  const best = Number(round.best_share || mining.best_share || 0);
  const candidatePct = Math.max(0, Math.min(100, Number(round.best_share_pct || mining.best_share_pct || (networkDiff ? best / networkDiff * 100 : 0))));
  const roundHeight = Number(round.height || data.job?.height || node.height || 0);
  const targetSeconds = Number(round.target_seconds || 600);
  const started = round.started_at ? Date.parse(round.started_at.replace(" ", "T") + "Z") : 0;
  const age = started ? Math.max(0, Math.floor((now - started) / 1000)) : 0;
  const remain = Math.max(0, targetSeconds - age);
  const remainPct = targetSeconds ? (remain / targetSeconds) * 100 : 0;
  const networkHash = Number(data.competition?.network_hashrate || node.network_hashrate || 0);
  const hashrate = Number(mining.hashrate_5m || 0);
  const luck = networkHash > 0 && hashrate > 0 ? (hashrate / networkHash) * 100 : 0;
  const sharesPerMin = Number(mining.round_shares || 0) / Math.max(1, age / 60);
  const blocks = useMemo(() => Array.isArray(data.blocks) ? data.blocks.slice(0, 8) : [], [data.blocks]);
  const shares = useMemo(() => Array.isArray(data.shares) ? data.shares.slice(-6).reverse() : [], [data.shares]);
  const uptime = node.online ? "ONLINE" : error ? "DEGRADED" : "STARTING";

  return <main className="appShell">
    <aside className="rail">
      <div className="crest">✦</div>
      <div className="brand">FIXEDCOIN<small>SOLO NODE</small></div>
      <div className="railLine" />
      <nav>{["Dashboard", "Mining", "Shares", "Blocks", "Workers", "Settings", "Logs", "System"].map((x, i) => <div className={`navItem ${i === 0 ? "active" : ""}`} key={x}><span>{["✦", "◇", "◌", "▣", "♙", "⚙", "≡", "⬡"][i]}</span>{x}</div>)}</nav>
      <div className="railGem"><Crystal small /></div>
      <div className="railStatus"><label>NODE STATUS</label><b className={node.online ? "ok" : "warn"}><i /> {uptime}</b><label>HEIGHT</label><strong>#{fmt(roundHeight, 0)}</strong><label>WORKERS</label><strong>{fmt(mining.worker_count, 0)}</strong></div>
    </aside>

    <section className="main">
      <header className="topbar"><div className="title">LIVESHARE <span>✦</span> ARCANE FORGE</div><div className={`live ${node.online ? "" : "offline"}`}><i /> STRATUM · {node.online ? "LIVE" : "OFFLINE"}</div></header>

      <section className="hero panel">
        <Dragon side="left" /><Dragon side="right" />
        <div className="heroCenter">
          <div className="kicker">ARCANE SOLO MINING NETWORK</div><h1>LIVESHARE</h1><div className="sub">SOLO MINING · MAGICAL NETWORK</div>
          <div className="versus">
            <div className="heroStat purple"><label>BEST SHARE DIFFICULTY</label><strong>{diff(best)}</strong><em>Best: {fmt(best, 0)}</em><div className="bar"><i style={{ width: `${candidatePct}%` }} /></div><small>{candidatePct.toFixed(2)}% of Network Target</small></div>
            <div className="vs">VS</div>
            <div className="heroStat gold"><label>NETWORK TARGET DIFFICULTY</label><strong>{diff(networkDiff)}</strong><em>{fmt(networkDiff, 0)}</em><div className="bar goldbar"><i style={{ width: `${candidatePct}%` }} /></div><small>{fmt(Math.max(0, networkDiff - best), 0)} remaining ({candidatePct.toFixed(2)}%)</small></div>
          </div>
        </div>
        <aside className="roundCard"><label>CURRENT ROUND</label><strong>#{fmt(roundHeight, 0)}</strong><span>⌛ ROUND AGE</span><b>{Math.floor(age / 60)}m {age % 60}s</b><span>⌛ TIME REMAINING</span><b className="cyan">{String(Math.floor(remain / 60)).padStart(2, "0")}:{String(remain % 60).padStart(2, "0")}</b><div className="statusBadge">{roundHeight ? "ACTIVE" : "WAITING"}</div><div className="roundBar"><i style={{ width: `${remainPct}%` }} /></div></aside>
      </section>

      <section className="forge panel">
        <div className="strip"><span>LIVE SHARE FORGE · REALTIME PROOF OF WORK</span><b>● {hash(hashrate)}</b></div>
        <div className="forgeGrid">
          <div className="metricStack">
            <Metric label="HASHRATE" value={hash(hashrate)} hint="LIVE PERFORMANCE" />
            <Metric label="SHARES / MIN" value={sharesPerMin ? fmt(sharesPerMin, 1) : "0.0"} hint="CURRENT ROUND" />
            <Metric label="NETWORK LUCK" value={luck ? `${luck.toFixed(1)}%` : "—"} hint="BASED ON NODE HASHRATE" gold />
          </div>
          <div className="altar"><div className="orbit o1" /><div className="orbit o2" /><div className="orbit o3" /><div className="altarGlow" /><Crystal /><div className="pedestal" /><strong>LIVESHARE <span>· ARCANE CORE</span></strong><small>MAGIC ENERGY // LIVE HASH STREAM // SHA256</small></div>
          <div className="metricStack">
            <Metric label="ACCEPTED SHARES" value={fmt(mining.accepted, 0)} hint={`${(100 - Number(mining.reject_pct || 0)).toFixed(2)}% ACCEPTANCE`} green />
            <Metric label="REJECTED SHARES" value={fmt(mining.rejected, 0)} hint={`${Number(mining.reject_pct || 0).toFixed(2)}% REJECT RATE`} red />
            <Metric label="LIVE WORKERS" value={fmt(mining.worker_count, 0)} hint="CONNECTED" />
          </div>
        </div>
        <div className="forgeFooter"><span>LAST SHARES</span>{shares.map((s, i) => <span className="sharePill" key={`${s.num}-${i}`}>✓ {s.worker ? short(s.worker.split(".").pop(), 9) : "share"} · {timeAgo(s.ts)}</span>)}</div>
      </section>

      <section className="lowerGrid">
        <article className="candidate panel"><header><span>✦</span><div><h2>BLOCK CANDIDATE</h2><small>Probability of a New Block</small></div></header><div className="candidateBody"><strong>{candidatePct.toFixed(3)}%</strong><small>PROGRESS TO BLOCK · BEST SHARE #{fmt(best, 0)}</small><div className="bar"><i style={{ width: `${candidatePct}%` }} /></div><Crystal small /></div></article>
        <article className="balance panel"><header><span>◇</span><div><h2>BALANCE</h2><small>Your Magical Earnings</small></div></header><div className="balanceBody"><strong>{Number(wallet.total || 0).toFixed(6)}</strong><b>FIX</b><small>CONFIRMED {Number(wallet.confirmed || 0).toFixed(6)} · PENDING {Number(wallet.pending || 0).toFixed(6)}</small><div className="scales">⚖</div></div></article>
      </section>

      <section className="history panel"><header><div><span>✦</span><h2>BLOCK HISTORY</h2><small>Chronicles of the Eternal Chain</small></div><b>{blocks.length} RECORDS</b></header><div className="tableWrap"><table><thead><tr><th>HEIGHT</th><th>TIME</th><th>DIFFICULTY</th><th>LUCK</th><th>SHARES</th><th>MINER</th><th>MAGIC HASH</th><th>REWARD</th></tr></thead><tbody>{blocks.length ? blocks.map((b, i) => <tr key={`${b.height}-${i}`}><td>#{fmt(b.height, 0)}</td><td>{b.time ? new Date(Number(b.time) * 1000).toLocaleTimeString() : "—"}</td><td>{diff(b.difficulty || networkDiff)}</td><td className="green">{Number.isFinite(Number(b.luck)) ? `+${Number(b.luck).toFixed(1)}%` : "—"}</td><td>{fmt(b.shares, 0)}</td><td>{short(b.miner, 14)}</td><td className="mono">{short(b.hash || b.blockhash, 18)}</td><td className="goldText">{Number(b.reward || 0).toFixed(4)} FIX</td></tr>) : <tr><td colSpan={8} className="empty">No block records yet — mining telemetry is live.</td></tr>}</tbody></table></div></section>

      <footer className="footer"><span>LIVESHARE · FIXEDCOIN SOLO</span><span>NODE {node.synced ? "SYNCED" : "SYNCING"} · HEIGHT #{fmt(roundHeight, 0)}</span><span>SHA-256</span><span>UPDATED {data.ts ? new Date(Number(data.ts) * 1000).toLocaleTimeString() : "—"}</span></footer>
    </section>
  </main>;
}

function Metric({ label, value, hint, gold, green, red }: { label: string; value: string; hint: string; gold?: boolean; green?: boolean; red?: boolean }) {
  return <div className={`metric ${gold ? "gold" : ""} ${green ? "green" : ""} ${red ? "red" : ""}`}><label>{label}</label><strong>{value}</strong><small>{hint}</small><div className="spark"><i /><i /><i /><i /><i /></div></div>;
}
