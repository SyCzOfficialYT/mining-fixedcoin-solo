export function HashrateBars({ miner, network }: { miner: number; network: number }) {
  const share = network > 0 ? (miner / network) * 100 : 0;
  const width = Math.max(Math.min(share * 10_000, 100), 0.75);

  return (
    <section className="panel p-5 lg:p-6">
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <p className="eyebrow">Hashrate ratio</p>
          <h2 className="section-title">Your slice of BCH</h2>
        </div>
        <span className="mono-label">NETWORK SHARE</span>
      </div>

      <div className="space-y-5">
        <div>
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="text-white/55">NerdQAxe++</span>
            <span className="font-medium text-[#7cf8ff]">{share.toExponential(3)}%</span>
          </div>
          <div className="h-2.5 overflow-hidden rounded-full bg-white/[0.06]">
            <div
              className="h-full rounded-full bg-[linear-gradient(90deg,#00a8c9,#7cf8ff)] shadow-[0_0_22px_rgba(0,229,255,0.35)] transition-all duration-700"
              style={{ width: `${width}%` }}
            />
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          <div className="metric-box">
            <span>Miner share</span>
            <strong>{share.toExponential(3)}%</strong>
          </div>
          <div className="metric-box">
            <span>Relative scale</span>
            <strong>1 : {(network / Math.max(miner, 1)).toLocaleString("en-US", { maximumFractionDigits: 0 })}</strong>
          </div>
          <div className="metric-box">
            <span>Mode</span>
            <strong>Solo-ready</strong>
          </div>
        </div>
      </div>
    </section>
  );
}
