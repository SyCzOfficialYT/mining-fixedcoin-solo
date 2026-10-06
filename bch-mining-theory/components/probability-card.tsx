import { formatProbability, type ProbabilityWindow } from "../lib/mining";

export function ProbabilityCard({ windows }: { windows: ProbabilityWindow[] }) {
  const max = Math.max(...windows.map((window) => window.probability), 1e-20);

  return (
    <section className="panel p-5 lg:p-6">
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <p className="eyebrow">Probability</p>
          <h2 className="section-title">Chance of ≥ 1 block</h2>
        </div>
        <span className="mono-label">POISSON</span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {windows.map((window) => (
          <div key={window.label} className="probability-tile">
            <div className="flex items-center justify-between gap-3">
              <span className="tile-label">{window.label}</span>
              <span className="tile-percent">{formatProbability(window.probability)}</span>
            </div>
            <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
              <div
                className="h-full rounded-full bg-[linear-gradient(90deg,#00e5ff,#7cf8ff)] transition-all duration-700"
                style={{ width: `${Math.max((window.probability / max) * 100, window.probability > 0 ? 4 : 0)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
