"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "motion/react";
import { HashrateBars } from "./hashrate-bars";
import { ProbabilityCard } from "./probability-card";
import { StatCard } from "./stat-card";
import {
  expectedBlockSeconds,
  expectedCoinPerDay,
  expectedBlocksPerDay,
  formatDifficulty,
  formatDuration,
  formatHashrate,
  probabilityWindows,
} from "../lib/mining";
import type { BchNetwork } from "../types/bch";

const defaultHashrate = Number(process.env.NEXT_PUBLIC_MINER_HASHRATE ?? 4_800_000_000_000);
const defaultReward = Number(process.env.NEXT_PUBLIC_BCH_BLOCK_REWARD ?? 3.125);

export function MiningDashboard() {
  const [network, setNetwork] = useState<BchNetwork | null>(null);
  const [offline, setOffline] = useState(false);
  const [minerHashrate, setMinerHashrate] = useState(defaultHashrate);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await fetch("/api/bch/network", { cache: "no-store" });
        if (!response.ok) throw new Error("BCH network unavailable");
        const data = (await response.json()) as BchNetwork;
        setNetwork(data);
        setOffline(false);
        setLastUpdated(new Date(data.fetchedAt).toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit", second: "2-digit" }));
      } catch {
        setOffline(true);
      }
    };

    void load();
    const timer = window.setInterval(load, 30_000);
    return () => window.clearInterval(timer);
  }, []);

  const metrics = useMemo(() => {
    const difficulty = network?.difficulty ?? 0;
    const networkHashrate = network?.networkHashrate ?? 0;
    const expectedSeconds = expectedBlockSeconds(difficulty, minerHashrate);
    return {
      difficulty,
      networkHashrate,
      expectedSeconds,
      expectedBlocksDay: expectedBlocksPerDay(difficulty, minerHashrate),
      expectedBchDay: expectedCoinPerDay(difficulty, minerHashrate, defaultReward),
      windows: probabilityWindows(difficulty, minerHashrate),
    };
  }, [minerHashrate, network]);

  return (
    <main className="relative min-h-screen overflow-hidden px-4 py-5 sm:px-6 lg:px-10">
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />

      <div className="mx-auto max-w-[1500px]">
        <header className="mb-8 flex flex-col gap-5 lg:mb-10 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="mb-3 flex items-center gap-3">
              <div className="brand-mark">₿</div>
              <span className="eyebrow">BCH / SHA-256D</span>
              <span className={`live-badge ${offline ? "is-offline" : ""}`}>
                <span className="pulse-dot" />
                {offline ? "OFFLINE" : "LIVE"}
              </span>
            </div>
            <h1 className="hero-title">Mining Theory</h1>
            <p className="hero-copy">
              A live Bitcoin Cash probability dashboard built around your actual miner hashrate.
            </p>
          </div>

          <div className="panel-soft w-full max-w-xl p-4">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="eyebrow">Miner profile</p>
                <p className="mt-1 text-sm text-white/60">NerdQAxe++ · SHA-256 ASIC</p>
              </div>
              <label className="flex items-center gap-3">
                <span className="text-xs font-medium uppercase tracking-[0.15em] text-white/35">Hashrate</span>
                <input
                  value={(minerHashrate / 1e12).toFixed(2)}
                  onChange={(event) => setMinerHashrate(Math.max(0, Number(event.target.value || 0)) * 1e12)}
                  inputMode="decimal"
                  className="field w-28"
                  aria-label="Miner hashrate in TH/s"
                />
                <span className="text-sm text-white/40">TH/s</span>
              </label>
            </div>
          </div>
        </header>

        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
          className="mb-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4"
        >
          <StatCard eyebrow="Your hashrate" value={formatHashrate(minerHashrate)} detail="Configured miner output" icon="⚡" />
          <StatCard eyebrow="BCH network" value={formatHashrate(metrics.networkHashrate)} detail="Estimated network hashrate" icon="◎" />
          <StatCard eyebrow="Difficulty" value={formatDifficulty(metrics.difficulty)} detail="Current BCH network difficulty" icon="◈" />
          <StatCard eyebrow="Block subsidy" value={`${defaultReward.toFixed(3)} BCH`} detail="Transaction fees excluded" icon="◐" />
        </motion.section>

        <section className="mb-4 grid gap-4 xl:grid-cols-[1.35fr_0.65fr]">
          <ProbabilityCard windows={metrics.windows} />

          <section className="panel p-5 lg:p-6">
            <p className="eyebrow">Expected value</p>
            <h2 className="section-title">Your miner outlook</h2>
            <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
              <div className="metric-box-large">
                <span>Expected block time</span>
                <strong>{metrics.difficulty > 0 ? formatDuration(metrics.expectedSeconds) : "Waiting for node"}</strong>
              </div>
              <div className="metric-box-large">
                <span>Expected blocks / day</span>
                <strong>{metrics.expectedBlocksDay > 0 ? metrics.expectedBlocksDay.toExponential(3) : "—"}</strong>
              </div>
              <div className="metric-box-large">
                <span>Expected BCH / day</span>
                <strong>{metrics.expectedBchDay > 0 ? metrics.expectedBchDay.toExponential(3) : "—"}</strong>
              </div>
            </div>
          </section>
        </section>

        <section className="mb-4">
          <HashrateBars miner={minerHashrate} network={metrics.networkHashrate} />
        </section>

        <section className="grid gap-4 lg:grid-cols-[1fr_1fr]">
          <section className="panel p-5 lg:p-6">
            <div className="mb-5 flex items-end justify-between gap-3">
              <div>
                <p className="eyebrow">Chain state</p>
                <h2 className="section-title">Current BCH network</h2>
              </div>
              {lastUpdated && <span className="mono-label">UPDATED {lastUpdated}</span>}
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="metric-box">
                <span>Chain</span>
                <strong>{network?.chain ?? "—"}</strong>
              </div>
              <div className="metric-box">
                <span>Block height</span>
                <strong>{network?.blocks?.toLocaleString("en-US") ?? "—"}</strong>
              </div>
              <div className="metric-box sm:col-span-2">
                <span>Best block</span>
                <strong className="break-all text-left text-sm font-medium">{network?.bestBlockHash || "—"}</strong>
              </div>
            </div>
          </section>

          <section className="panel p-5 lg:p-6">
            <p className="eyebrow">Methodology</p>
            <h2 className="section-title">How the probability is calculated</h2>
            <div className="mt-5 space-y-4 text-sm leading-6 text-white/55">
              <p>Difficulty is converted into the expected number of SHA-256d hashes using 2³² hashes per difficulty-1 unit.</p>
              <p>Block chance uses a Poisson model: <span className="formula">P(X ≥ 1) = 1 − e<sup>−λ</sup></span>.</p>
              <p>Expected BCH per day uses the current subsidy only. Realized blocks also carry transaction fees, which are intentionally excluded from the baseline estimate.</p>
            </div>
          </section>
        </section>

        <footer className="mt-7 flex flex-col gap-2 border-t border-white/[0.06] py-5 text-xs text-white/30 sm:flex-row sm:items-center sm:justify-between">
          <span>BCH Mining Theory · built for private/self-hosted BCH nodes</span>
          <span>{offline ? "Connect BCHN RPC to enable live network data" : "Auto-refresh every 30 seconds"}</span>
        </footer>
      </div>
    </main>
  );
}
