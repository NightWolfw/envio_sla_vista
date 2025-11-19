"use client";

import { useEffect, useState } from "react";

type ResumoData = {
  finalizadas: number;
  nao_realizadas: number;
  em_aberto: number;
  iniciadas: number;
};

type ResumoPayload = {
  data: ResumoData | null;
  periodo?: {
    descricao?: string;
    inicio?: string;
    fim?: string;
    label?: string;
  };
};

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.API_BASE_URL ?? "http://localhost:5000/api";
const DEFAULT_DIRETOR = "MARCOS NASCIMENTO PEDREIRA";

export default function DashboardResumoClient() {
  const [data, setData] = useState<ResumoData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [referencia, setReferencia] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function fetchResumo() {
      try {
        const params = new URLSearchParams({ diretor_executivo: DEFAULT_DIRETOR });
        const res = await fetch(`${API_BASE}/dashboard/resumo?${params.toString()}`, {
          cache: "no-store"
        });
        if (!res.ok) {
          throw new Error(await res.text());
        }
        const payload: ResumoPayload = await res.json();
        if (!cancelled) {
          setData(payload.data ?? null);
          setReferencia(payload.periodo?.label ?? payload.periodo?.descricao ?? null);
          setIsLoading(false);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(
            err?.message ??
              "Não foi possível carregar os indicadores de SLA. Tente novamente mais tarde."
          );
          setIsLoading(false);
        }
      }
    }
    fetchResumo();
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <section className="panel">
        <h2>Desempenho SLA (MARCOS NASCIMENTO PEDREIRA)</h2>
        <p>{error}</p>
      </section>
    );
  }

  if (isLoading) {
    return (
      <section className="panel">
        <h2>Desempenho SLA (MARCOS NASCIMENTO PEDREIRA)</h2>
        <div className="skeleton shimmer" />
      </section>
    );
  }

  const safeData: ResumoData = data ?? {
    finalizadas: 0,
    nao_realizadas: 0,
    em_aberto: 0,
    iniciadas: 0
  };

  const resumoCards = [
    { label: "Finalizadas", value: safeData.finalizadas ?? 0 },
    { label: "Não realizadas", value: safeData.nao_realizadas ?? 0 },
    { label: "Em aberto", value: safeData.em_aberto ?? 0 },
    { label: "Iniciadas", value: safeData.iniciadas ?? 0 }
  ];

  return (
    <section className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2>Desempenho SLA ({DEFAULT_DIRETOR})</h2>
        {referencia && <span style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>Referência: {referencia}</span>}
      </div>
      <div className="grid cards">
        {resumoCards.map((card) => (
          <div key={card.label} className="panel" style={{ padding: "1rem" }}>
            <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "0.9rem" }}>{card.label}</p>
            <strong style={{ fontSize: "1.6rem" }}>{card.value}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
