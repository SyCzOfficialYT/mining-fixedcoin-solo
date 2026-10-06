import type { ReactNode } from "react";

export function StatCard({
  eyebrow,
  value,
  detail,
  icon,
}: {
  eyebrow: string;
  value: string;
  detail: string;
  icon: ReactNode;
}) {
  return (
    <section className="panel p-5">
      <div className="mb-6 flex items-start justify-between gap-4">
        <p className="eyebrow">{eyebrow}</p>
        <div className="icon-box">{icon}</div>
      </div>
      <p className="stat-value">{value}</p>
      <p className="stat-detail">{detail}</p>
    </section>
  );
}
