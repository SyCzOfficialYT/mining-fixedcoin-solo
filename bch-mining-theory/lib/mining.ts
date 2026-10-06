const HASHES_PER_DIFFICULTY_1 = 2 ** 32;

export type ProbabilityWindow = {
  label: string;
  seconds: number;
  probability: number;
};

export function expectedBlockSeconds(
  difficulty: number,
  hashrate: number,
): number {
  if (!Number.isFinite(difficulty) || !Number.isFinite(hashrate)) return Infinity;
  if (difficulty <= 0 || hashrate <= 0) return Infinity;
  return (difficulty * HASHES_PER_DIFFICULTY_1) / hashrate;
}

export function blockProbability(
  difficulty: number,
  hashrate: number,
  seconds: number,
): number {
  const expected = expectedBlockSeconds(difficulty, hashrate);
  if (!Number.isFinite(expected) || seconds <= 0) return 0;
  const lambda = seconds / expected;
  return 1 - Math.exp(-lambda);
}

export function expectedBlocksPerDay(
  difficulty: number,
  hashrate: number,
): number {
  const expected = expectedBlockSeconds(difficulty, hashrate);
  if (!Number.isFinite(expected)) return 0;
  return 86_400 / expected;
}

export function expectedCoinPerDay(
  difficulty: number,
  hashrate: number,
  reward: number,
): number {
  return expectedBlocksPerDay(difficulty, hashrate) * reward;
}

export function networkShare(
  hashrate: number,
  networkHashrate: number,
): number {
  if (hashrate <= 0 || networkHashrate <= 0) return 0;
  return hashrate / networkHashrate;
}

export function probabilityWindows(
  difficulty: number,
  hashrate: number,
): ProbabilityWindow[] {
  return [
    ["1 H", 3_600],
    ["24 H", 86_400],
    ["7 D", 604_800],
    ["30 D", 2_592_000],
  ].map(([label, seconds]) => ({
    label: String(label),
    seconds: Number(seconds),
    probability: blockProbability(difficulty, hashrate, Number(seconds)),
  }));
}

export function formatHashrate(hashrate: number): string {
  if (!Number.isFinite(hashrate) || hashrate <= 0) return "—";
  const units = ["H/s", "KH/s", "MH/s", "GH/s", "TH/s", "PH/s", "EH/s"];
  let value = hashrate;
  let unit = 0;
  while (value >= 1_000 && unit < units.length - 1) {
    value /= 1_000;
    unit += 1;
  }
  const digits = value >= 100 ? 0 : value >= 10 ? 1 : 2;
  return `${value.toFixed(digits)} ${units[unit]}`;
}

export function formatDifficulty(difficulty: number): string {
  if (!Number.isFinite(difficulty) || difficulty <= 0) return "—";
  if (difficulty >= 1e18) return `${(difficulty / 1e18).toFixed(2)}E`;
  if (difficulty >= 1e15) return `${(difficulty / 1e15).toFixed(2)}P`;
  if (difficulty >= 1e12) return `${(difficulty / 1e12).toFixed(2)}T`;
  if (difficulty >= 1e9) return `${(difficulty / 1e9).toFixed(2)}G`;
  if (difficulty >= 1e6) return `${(difficulty / 1e6).toFixed(2)}M`;
  return difficulty.toLocaleString("en-US", { maximumFractionDigits: 2 });
}

export function formatDuration(seconds: number): string {
  if (!Number.isFinite(seconds)) return "∞";
  const days = seconds / 86_400;
  if (days >= 365) return `${(days / 365).toFixed(1)} y`;
  if (days >= 1) return `${days.toFixed(1)} d`;
  const hours = seconds / 3_600;
  if (hours >= 1) return `${hours.toFixed(1)} h`;
  const minutes = Math.max(seconds / 60, 0.1);
  return `${minutes.toFixed(1)} m`;
}

export function formatProbability(probability: number): string {
  const pct = Math.max(0, Math.min(probability * 100, 100));
  if (pct < 0.0001) return `${pct.toExponential(2)}%`;
  if (pct < 0.01) return `${pct.toFixed(4)}%`;
  if (pct < 1) return `${pct.toFixed(2)}%`;
  return `${pct.toFixed(1)}%`;
}
