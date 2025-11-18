"use client";

import type { OverviewStats } from "../lib/api";
import DashboardResumoClient from "./DashboardResumoClient";

type Props = {
  stats: OverviewStats;
};

export default function HomeContent({ stats }: Props) {
  const cards = [
    { label: "Grupos", value: stats.total_grupos },
    { label: "Mensagens ativas", value: stats.total_mensagens },
    { label: "Envios realizados", value: stats.total_envios }
  ];

  return (
    <div className="grid" style={{ gap: "1.5rem" }}>
      <section className="panel">
        <h2>Resumo rápido</h2>
        <div className="grid cards">
          {cards.map((card) => (
            <div key={card.label} className="panel" style={{ padding: "1rem" }}>
              <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "0.9rem" }}>{card.label}</p>
              <strong style={{ fontSize: "1.8rem" }}>{card.value}</strong>
            </div>
          ))}
        </div>
      </section>

      <DashboardResumoClient />
    </div>
  );
}
