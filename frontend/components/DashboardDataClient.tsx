"use client";

import { useEffect, useMemo, useState } from "react";
import {
  getDashboardConfig,
  getDashboardSla,
  syncDashboardSla,
  updateDashboardConfig,
  type DashboardSlaPayload,
  type DashboardConfig
} from "../lib/api";

type HeatCell = { cr: string; dia: string; valor: number };

const cardClass = "panel rounded-xl border border-border/60 bg-surface/60 p-4";
const btnPrimary =
  "rounded-lg bg-accent px-3 py-2 text-sm font-semibold text-[#0f172a] shadow hover:bg-cyan-300 transition disabled:opacity-50";
const btnGhost = "rounded-lg border border-border px-3 py-2 text-sm text-text hover:bg-surfaceMuted/40 transition";

export default function DashboardDataClient() {
  const [data, setData] = useState<DashboardSlaPayload | null>(null);
  const [config, setConfig] = useState<DashboardConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [savingConfig, setSavingConfig] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [showConfig, setShowConfig] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | undefined>(undefined);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [payload, cfg] = await Promise.all([getDashboardSla(), getDashboardConfig()]);
        if (cancelled) return;
        setData(payload.data);
        setLastUpdated(payload.last_updated);
        setConfig(cfg.data);
      } catch (err: any) {
        if (!cancelled) setError(err?.message ?? "Falha ao carregar dashboard");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    setError(null);
    try {
      const payload = await syncDashboardSla();
      setData(payload.data);
      setLastUpdated(payload.last_updated);
    } catch (err: any) {
      setError(err?.message ?? "Falha ao sincronizar");
    } finally {
      setSyncing(false);
    }
  };

  const handleSaveConfig = async (newConfig: { hora_inicio: string; hora_fim: string; intervalo_minutos: number }) => {
    setSavingConfig(true);
    setError(null);
    try {
      const res = await updateDashboardConfig(newConfig);
      setConfig(res.data);
    } catch (err: any) {
      setError(err?.message ?? "Falha ao salvar configuração");
    } finally {
      setSavingConfig(false);
      setShowConfig(false);
    }
  };

  const heatCells: HeatCell[] = useMemo(() => {
    if (!data) return [];
    const rows: HeatCell[] = [];
    data.heatmap.forEach((crItem) => {
      Object.entries(crItem.dias || {}).forEach(([dia, valor]) => {
        rows.push({ cr: crItem.cr, dia: String(dia), valor: Number(valor) });
      });
    });
    return rows;
  }, [data]);

  const ultimoAtualizado = lastUpdated
    ? new Date(lastUpdated).toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo" })
    : "—";

  if (loading) {
    return (
      <div className="grid gap-4">
        <div className={`${cardClass} h-28 animate-pulse`} />
        <div className={`${cardClass} h-64 animate-pulse`} />
        <div className={`${cardClass} h-64 animate-pulse`} />
      </div>
    );
  }

  if (error) {
    return (
      <section className={cardClass}>
        <h2 className="text-lg font-semibold">Dashboard</h2>
        <p className="text-sm text-rose-300">{error}</p>
        <button onClick={handleSync} className={`${btnPrimary} mt-3`} disabled={syncing}>
          {syncing ? "Sincronizando..." : "Sincronizar agora"}
        </button>
      </section>
    );
  }

  if (!data) return null;

  return (
    <div className="grid gap-4">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold text-text">Dashboard SLA</h1>
          <p className="text-sm text-textMuted">Diretor executivo travado: MARCOS NASCIMENTO PEDREIRA</p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-sm text-textMuted">
          <span>Última atualização: {ultimoAtualizado}</span>
          <button onClick={() => setShowFilters((v) => !v)} className={btnGhost} title="Filtros">
            Filtros
          </button>
          <button onClick={() => setShowConfig((v) => !v)} className={btnGhost} title="Configurações">
            Configurações
          </button>
          <button onClick={handleSync} className={btnPrimary} disabled={syncing}>
            {syncing ? "Sincronizando..." : "Sincronizar agora"}
          </button>
        </div>
      </header>

      {showFilters && (
        <section className={cardClass}>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-text">Filtros</h3>
            <button className={btnGhost} onClick={() => setShowFilters(false)}>
              Fechar
            </button>
          </div>
          <p className="text-xs text-textMuted mt-2">Diretor Executivo: MARCOS NASCIMENTO PEDREIRA (fixo)</p>
          <p className="text-xs text-textMuted">Demais filtros serão aplicados sobre o cache atual.</p>
        </section>
      )}

      {showConfig && config && (
        <section className={cardClass}>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-text">Configuração de atualização</h3>
            <button className={btnGhost} onClick={() => setShowConfig(false)}>
              Fechar
            </button>
          </div>
          <div className="mt-3 grid gap-3 md:grid-cols-3">
            <label className="text-sm text-text">
              Início (HH:MM)
              <input
                type="time"
                defaultValue={config.hora_inicio}
                className="mt-1 w-full rounded border border-border bg-surface px-2 py-1 text-sm"
                onChange={(e) => setConfig((prev) => (prev ? { ...prev, hora_inicio: e.target.value } : prev))}
              />
            </label>
            <label className="text-sm text-text">
              Fim (HH:MM)
              <input
                type="time"
                defaultValue={config.hora_fim}
                className="mt-1 w-full rounded border border-border bg-surface px-2 py-1 text-sm"
                onChange={(e) => setConfig((prev) => (prev ? { ...prev, hora_fim: e.target.value } : prev))}
              />
            </label>
            <label className="text-sm text-text">
              Intervalo (min)
              <input
                type="number"
                min={1}
                defaultValue={config.intervalo_minutos}
                className="mt-1 w-full rounded border border-border bg-surface px-2 py-1 text-sm"
                onChange={(e) =>
                  setConfig((prev) =>
                    prev ? { ...prev, intervalo_minutos: Number(e.target.value || 10) } : prev
                  )
                }
              />
            </label>
          </div>
          <div className="mt-3 flex justify-end gap-2">
            <button className={btnGhost} onClick={() => setShowConfig(false)}>
              Cancelar
            </button>
            <button
              className={btnPrimary}
              disabled={savingConfig}
              onClick={() =>
                handleSaveConfig({
                  hora_inicio: config.hora_inicio,
                  hora_fim: config.hora_fim,
                  intervalo_minutos: config.intervalo_minutos
                })
              }
            >
              {savingConfig ? "Salvando..." : "Salvar"}
            </button>
          </div>
        </section>
      )}

      <section className={cardClass}>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-text">Tarefas por dia (mês atual)</h3>
          <span className="text-xs text-textMuted">{data.periodo.descricao}</span>
        </div>
        <div className="mt-4 flex items-end gap-2 overflow-x-auto">
          {data.serie_diaria.map((item) => {
            const valor = item.total || 0;
            const height = Math.min(160, 8 + valor * 6);
            const diaLabel = new Date(item.dia).getDate();
            return (
              <div key={item.dia} className="flex flex-col items-center text-xs text-textMuted">
                <div
                  className="w-6 rounded-t bg-accent"
                  style={{ height, minHeight: 12, transition: "height 0.2s" }}
                  title={`${valor} tarefas`}
                />
                <span className="mt-1">{diaLabel}</span>
              </div>
            );
          })}
        </div>
      </section>

      <section className={cardClass}>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-text">Tarefas por mês (últimos 6 meses)</h3>
        </div>
        <div className="mt-4 flex items-end gap-3 overflow-x-auto">
          {data.serie_mensal.map((item) => {
            const valor = item.total || 0;
            const height = Math.min(180, 10 + valor * 4);
            const labelDate = new Date(item.mes + "T00:00:00");
            const label = `${String(labelDate.getMonth() + 1).padStart(2, "0")}/${labelDate.getFullYear()}`;
            return (
              <div key={item.mes} className="flex flex-col items-center text-xs text-textMuted">
                <div
                  className="w-8 rounded-t bg-accent"
                  style={{ height, minHeight: 14, transition: "height 0.2s" }}
                  title={`${valor} tarefas`}
                />
                <span className="mt-1">{label}</span>
              </div>
            );
          })}
        </div>
      </section>

      <section className={cardClass}>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-text">Heatmap SLA (CR x Dia)</h3>
          <p className="text-xs text-textMuted">Verde &gt;=90 • Amarelo 65-89.9 • Vermelho &lt;65</p>
        </div>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-xs text-text">
            <thead>
              <tr>
                <th className="px-2 py-1 text-left">CR</th>
                {Array.from(new Set(heatCells.map((c) => c.dia)))
                  .sort((a, b) => Number(a) - Number(b))
                  .map((dia) => (
                    <th key={dia} className="px-2 py-1 text-center">
                      {dia}
                    </th>
                  ))}
              </tr>
            </thead>
            <tbody>
              {data.heatmap.map((row) => (
                <tr key={row.cr}>
                  <td className="px-2 py-1 font-semibold">{row.cr}</td>
                  {Array.from(new Set(heatCells.map((c) => c.dia)))
                    .sort((a, b) => Number(a) - Number(b))
                    .map((dia) => {
                      const valor = row.dias?.[dia] ?? row.dias?.[Number(dia)] ?? 0;
                      const cor =
                        valor >= 90 ? "#16a34a" : valor >= 65 ? "#eab308" : "#dc2626";
                      return (
                        <td key={dia} className="px-1 py-1 text-center">
                          <div
                            className="rounded text-[11px] font-semibold text-white"
                            style={{
                              background: cor,
                              minWidth: 32,
                              padding: "4px 6px"
                            }}
                            title={`${valor}%`}
                          >
                            {valor}%
                          </div>
                        </td>
                      );
                    })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className={cardClass}>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-text">Finalizadas x Não realizadas</h3>
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-6 text-sm">
          <div className="flex flex-col gap-2">
            <span className="font-semibold text-text">Finalizadas</span>
            <span className="text-emerald-300 text-lg">{data.pizza.finalizadas}</span>
          </div>
          <div className="flex flex-col gap-2">
            <span className="font-semibold text-text">Não realizadas</span>
            <span className="text-rose-300 text-lg">{data.pizza.nao_realizadas}</span>
          </div>
          <div className="flex flex-col gap-2">
            <span className="font-semibold text-text">Total</span>
            <span className="text-text text-lg">{data.pizza.total}</span>
          </div>
        </div>
      </section>
    </div>
  );
}
