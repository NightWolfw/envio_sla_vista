"use client";

import { useEffect, useState } from "react";
import { getDashboardResumo, getDashboardTarefas, getDashboardPizza } from "../lib/api";

type ResumoResponse = Awaited<ReturnType<typeof getDashboardResumo>>;
type TarefasResponse = Awaited<ReturnType<typeof getDashboardTarefas>>;
type PizzaResponse = Awaited<ReturnType<typeof getDashboardPizza>>;

export default function DashboardDataClient() {
  const [resumo, setResumo] = useState<ResumoResponse | null>(null);
  const [tarefas, setTarefas] = useState<TarefasResponse | null>(null);
  const [pizza, setPizza] = useState<PizzaResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function fetchData() {
      try {
        const [r, t, p] = await Promise.all([
          getDashboardResumo(),
          getDashboardTarefas(),
          getDashboardPizza()
        ]);
        if (!cancelled) {
          setResumo(r);
          setTarefas(t);
          setPizza(p);
          setLoading(false);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err?.message ?? "Falha ao carregar dashboard");
          setLoading(false);
        }
      }
    }
    fetchData();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="grid" style={{ gap: "1.5rem" }}>
        <section className="panel">
          <h2>Resumo geral</h2>
          <div className="skeleton shimmer" />
        </section>
        <section className="panel">
          <h2>Tarefas por dia</h2>
          <div className="skeleton shimmer" style={{ height: 180 }} />
        </section>
        <section className="panel">
          <h2>Distribuição por status</h2>
          <div className="skeleton shimmer" style={{ height: 120 }} />
        </section>
      </div>
    );
  }

  if (error) {
    return (
      <section className="panel">
        <h2>Dashboard</h2>
        <p>{error}</p>
      </section>
    );
  }

  const pizzaData = Array.isArray(pizza?.data)
    ? pizza?.data
    : Object.entries(pizza?.data ?? {}).map(([status, total]) => ({
        status,
        total,
        cor: ""
      }));

  return (
    <div className="grid" style={{ gap: "1.5rem" }}>
      <section className="panel">
        <h2>Resumo geral</h2>
        <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>{JSON.stringify(resumo?.data, null, 2)}</pre>
      </section>

      <section className="panel">
        <h2>Tarefas por dia (mês atual)</h2>
        <table>
          <thead>
            <tr>
              <th>Dia</th>
              <th>Finalizadas</th>
              <th>Não realizadas</th>
              <th>Em aberto</th>
              <th>Iniciadas</th>
            </tr>
          </thead>
          <tbody>
            {(tarefas?.data ?? []).map((item, idx) => (
              <tr key={idx}>
                <td>{item.dia}</td>
                <td>{item.finalizadas}</td>
                <td>{item.nao_realizadas}</td>
                <td>{item.em_aberto}</td>
                <td>{item.iniciadas}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="panel">
        <h2>Distribuição por status</h2>
        <table>
          <tbody>
            {pizzaData.map((item: any, idx: number) => (
              <tr key={idx}>
                <td style={{ textTransform: "capitalize" }}>{item.status?.toString().replace("_", " ")}</td>
                <td>{item.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
