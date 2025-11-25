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
  "inline-flex items-center gap-2 rounded-lg bg-accent px-3 py-2 text-sm font-semibold text-[#0f172a] shadow hover:bg-cyan-300 transition disabled:opacity-50";
const btnGhost =
  "inline-flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm text-text hover:bg-surfaceMuted/40 transition";

export default function DashboardDataClient() {
  const [data, setData] = useState<DashboardSlaPayload | null>(null);
  const [config, setConfig] = useState<DashboardConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [savingConfig, setSavingConfig] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [showDateFilters, setShowDateFilters] = useState(false);
  const [showConfig, setShowConfig] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | undefined>(undefined);
  const [selectedMonth, setSelectedMonth] = useState<string | null>(null);
  const [textFilters, setTextFilters] = useState<Record<string, string>>({
    diretor_regional: "",
    gerente_regional: "",
    gerente: "",
    supervisor: "",
    cr: "",
    cliente: "",
    pec_01: "",
    pec_02: ""
  });

  const loadDashboard = async (filters?: Record<string, string | number | undefined | null>) => {
    setLoading(true);
    setError(null);
    try {
      const payload = await getDashboardSla(filters);
      if (!payload.success || !payload.data) {
        setData(null);
        setLastUpdated(undefined);
        setError("Dashboard ainda não foi sincronizado. Clique em \"Sincronizar agora\".");
        return;
      }
      setData(payload.data);
      setLastUpdated(payload.last_updated || payload.data?.last_updated);
      const cfg = await getDashboardConfig();
      setConfig(cfg.data);
    } catch (err: any) {
      setError(err?.message ?? "Falha ao carregar dashboard");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;
    async function load() {
      await loadDashboard();
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
      const payload = await syncDashboardSla(buildFiltersParams());
      // Garante que aplicamos os dados já escritos no Redis
      await loadDashboard(buildFiltersParams());
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

  const buildFiltersParams = () => {
    const params: Record<string, string> = {};
    Object.entries(textFilters).forEach(([k, v]) => {
      if (v) params[k] = v;
    });
    if (selectedMonth) {
      const d = new Date(selectedMonth + "-01T00:00:00");
      params["mes"] = String(d.getMonth() + 1);
      params["ano"] = String(d.getFullYear());
    }
    return params;
  };

  const applyFilters = () => {
    const params = buildFiltersParams();
    loadDashboard(params);
    setShowFilters(false);
    setShowDateFilters(false);
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
      <div className="flex min-h-[320px] flex-col items-center justify-center gap-3 rounded-xl border border-border/60 bg-surface/60 p-6 text-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-accent border-t-transparent" />
        <p className="text-sm font-semibold text-text">Carregando dados...</p>
        <p className="text-xs text-textMuted">Estimativa: alguns segundos</p>
      </div>
    );
  }

  if (error) {
    return (
      <section className={cardClass}>
        <h2 className="text-lg font-semibold">Dashboard</h2>
        <p className="text-sm text-rose-300">{error}</p>
        <button onClick={handleSync} className={`${btnPrimary} mt-3`} disabled={syncing}>
          {syncing ? "Sincronizando..." : 'Sincronizar agora'}
        </button>
      </section>
    );
  }

  if (!data) return null;

  const diasOrdenados = Array.from(
    new Set(heatCells.map((c) => Number(c.dia)))
  ).sort((a, b) => a - b);

  const monthOptions = data.serie_diaria
    .map((d) => d.dia.slice(0, 7))
    .filter((v, i, arr) => arr.indexOf(v) === i);
  const activeMonth = selectedMonth || data.periodo.inicio.slice(0, 7);

  const filteredDaily = data.serie_diaria.filter((item) => item.dia.startsWith(activeMonth));
  const dailyMax =
    Math.max(...filteredDaily.map((d) => (d.finalizadas || 0) + (d.nao_realizadas || 0)), 1);

  const heatmapFiltered = data.heatmap.filter((row) => {
    const t = textFilters;
    const match = (value: string, needle: string) =>
      !needle || value.toLowerCase().includes(needle.toLowerCase());
    return (
      match(row.cr, t.cr) &&
      match(row.cr, t.cliente) && // fallback: sem cliente no payload, usa cr como proxy
      match(row.cr, t.pec_01) &&
      match(row.cr, t.pec_02)
    );
  });

  const pctFinal = data.pizza.total ? Math.round((data.pizza.finalizadas / data.pizza.total) * 100) : 0;
  const pctNao = 100 - pctFinal;

  return (
    <div className="grid gap-4">
      <header className="sticky top-0 z-10 flex flex-wrap items-center justify-between gap-3 bg-surface/80 p-2 backdrop-blur">
        <div>
          <h1 className="text-xl font-semibold text-text">Dashboard SLA</h1>
          <p className="text-sm text-textMuted">Diretor executivo travado: MARCOS NASCIMENTO PEDREIRA</p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-sm text-text">
          <span className="text-xs text-textMuted">Última atualização (BRT): {ultimoAtualizado}</span>
          <button onClick={() => setShowFilters((v) => !v)} className={btnGhost} title="Filtros">
            <span role="img" aria-label="filtros">
              🧰
            </span>
          </button>
          <button onClick={() => setShowDateFilters((v) => !v)} className={btnGhost} title="Filtros de data">
            <span role="img" aria-label="data">
              📅
            </span>
          </button>
          <button onClick={() => setShowConfig((v) => !v)} className={btnGhost} title="Configurações">
            <span role="img" aria-label="config">
              ⚙️
            </span>
          </button>
          <button onClick={handleSync} className={btnPrimary} disabled={syncing} title="Sincronizar agora">
            <span role="img" aria-label="sync">
              🔄
            </span>
          </button>
        </div>
      </header>

      {showFilters && (
        <div className="fixed inset-0 z-20 bg-black/40 backdrop-blur-sm">
          <div className="absolute right-4 top-4 w-full max-w-md rounded-xl border border-border bg-surface p-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-text">Filtros</h3>
              <button className={btnGhost} onClick={() => setShowFilters(false)}>
                Fechar
              </button>
            </div>
            <p className="text-xs text-textMuted mt-2">Diretor Executivo: MARCOS NASCIMENTO PEDREIRA (fixo)</p>
            <div className="mt-3 grid gap-2">
              {[
                "diretor_regional",
                "gerente_regional",
                "gerente",
                "supervisor",
                "cr",
                "cliente",
                "pec_01",
                "pec_02"
              ].map((f) => (
                <label key={f} className="text-xs text-text flex flex-col gap-1">
                  {f.replace("_", " ").toUpperCase()}
                  <input
                    type="text"
                    placeholder={`Buscar ${f}`}
                    className="rounded border border-border bg-surface px-2 py-1 text-sm text-text"
                    value={textFilters[f] || ""}
                    onChange={(e) =>
                      setTextFilters((prev) => ({
                        ...prev,
                        [f]: e.target.value
                      }))
                    }
                  />
                </label>
              ))}
              <div className="mt-2 flex justify-end gap-2">
                <button className={btnGhost} onClick={() => setShowFilters(false)}>
                  Cancelar
                </button>
                <button className={btnPrimary} onClick={applyFilters}>
                  Aplicar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showDateFilters && (
        <div className="fixed inset-0 z-20 bg-black/40 backdrop-blur-sm">
          <div className="absolute right-4 top-4 w-full max-w-sm rounded-xl border border-border bg-surface p-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-text">Filtros de data</h3>
              <button className={btnGhost} onClick={() => setShowDateFilters(false)}>
                Fechar
              </button>
            </div>
            <div className="mt-3">
              <label className="text-sm text-text">
                Mês/Ano (últimos 6 meses)
                <select
                  className="mt-1 w-full rounded border border-border bg-surface px-2 py-1 text-sm"
                  value={activeMonth}
                  onChange={(e) => setSelectedMonth(e.target.value)}
                >
                  {monthOptions.map((m) => {
                    const d = new Date(m + "T00:00:00");
                    const label = `${String(d.getMonth() + 1).padStart(2, "0")}/${d.getFullYear()}`;
                    return (
                      <option key={m} value={m.slice(0, 7)}>
                        {label}
                      </option>
                    );
                  })}
                </select>
              </label>
              <div className="mt-3 flex justify-end gap-2">
                <button className={btnGhost} onClick={() => setShowDateFilters(false)}>
                  Cancelar
                </button>
                <button className={btnPrimary} onClick={applyFilters}>
                  Aplicar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showConfig && config && (
        <div className="fixed inset-0 z-20 bg-black/40 backdrop-blur-sm">
          <div className="absolute right-4 top-4 w-full max-w-md rounded-xl border border-border bg-surface p-4 shadow-2xl">
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
          </div>
        </div>
      )}

      <section className={cardClass}>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-text">Tarefas por dia (mês atual)</h3>
          <span className="text-xs text-textMuted">{data.periodo.descricao}</span>
        </div>
        <div className="mt-4 flex items-end gap-2 overflow-x-auto">
          {filteredDaily.map((item) => {
            const diaLabel = new Date(item.dia).getDate();
            const total = (item.finalizadas || 0) + (item.nao_realizadas || 0);
            const maxHeight = 200;
            const scale = maxHeight / (dailyMax || 1);
            const heightFinal = Math.max(4, (item.finalizadas || 0) * scale);
            const heightNao = Math.max(4, (item.nao_realizadas || 0) * scale);
            return (
              <div key={item.dia} className="flex flex-col items-center text-xs text-textMuted min-w-[28px]">
                <div className="flex w-6 flex-col-reverse overflow-hidden rounded" style={{ height: maxHeight }}>
                  <div
                    className="bg-rose-500/80"
                    style={{ height: heightNao }}
                    title={`Não realizadas: ${item.nao_realizadas || 0}`}
                  />
                  <div
                    className="bg-emerald-500/80"
                    style={{ height: heightFinal }}
                    title={`Finalizadas: ${item.finalizadas || 0}`}
                  />
                </div>
                <span className="mt-1">{diaLabel}</span>
                <span className="text-[10px] text-textMuted">{total}</span>
              </div>
            );
          })}
        </div>
      </section>

      <section className={cardClass}>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-text">Ranking de executores (mês atual)</h3>
          <span className="text-xs text-textMuted">Top executores por finalizações</span>
        </div>
        <div className="mt-3 max-h-72 overflow-y-auto">
          {data.ranking_executores && data.ranking_executores.length > 0 ? (
            <div className="space-y-2">
              {data.ranking_executores.map((item, idx) => {
                const total = item.total || 0;
                const final = item.finalizadas || 0;
                const nao = item.nao_realizadas || 0;
                const widthFinal = Math.min(100, (final / (total || 1)) * 100);
                const widthNao = Math.min(100, (nao / (total || 1)) * 100);
                return (
                  <div key={item.executor + idx} className="rounded border border-border/40 bg-surfaceMuted/30 p-2">
                    <div className="flex items-center justify-between text-xs text-text">
                      <span className="font-semibold text-text">{item.executor}</span>
                      <span className="text-textMuted">{total} tarefas</span>
                    </div>
                    <div className="mt-2 flex h-4 w-full overflow-hidden rounded bg-border/40">
                      <div
                        className="bg-emerald-500/80"
                        style={{ width: `${widthFinal}%` }}
                        title={`Finalizadas: ${final}`}
                      />
                      <div
                        className="bg-rose-500/80"
                        style={{ width: `${widthNao}%` }}
                        title={`Não realizadas: ${nao}`}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-textMuted">Sem dados de executores.</p>
          )}
        </div>
      </section>

      <section className={cardClass}>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-text">Heatmap SLA (CR x Dia)</h3>
          <p className="text-xs text-textMuted">Verde &gt;=90 • Amarelo 65-89.9 • Vermelho &lt;65</p>
        </div>
        <div className="mt-3 max-h-72 overflow-y-auto overflow-x-auto">
          <table className="w-full min-w-[640px] text-xs text-text">
            <thead className="sticky top-0 bg-surface">
              <tr>
                <th className="px-2 py-1 text-left">CR</th>
                {diasOrdenados.map((dia) => (
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
                  {diasOrdenados.map((dia) => {
                    const valor = row.dias?.[dia] ?? row.dias?.[String(dia)] ?? 0;
                    const cor = valor >= 90 ? "#16a34a" : valor >= 65 ? "#eab308" : "#dc2626";
                    return (
                      <td key={`${row.cr}-${dia}`} className="px-1 py-1 text-center">
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
          <div
            className="relative h-32 w-32 rounded-full"
            style={{
              background: `conic-gradient(#22c55e 0% ${pctFinal}%, #ef4444 ${pctFinal}% 100%)`
            }}
            title={`Finalizadas ${pctFinal}% | Não realizadas ${pctNao}%`}
          >
            <div className="absolute inset-3 rounded-full bg-surface flex items-center justify-center text-xs text-text">
              <div className="text-center">
                <div className="text-lg font-semibold text-text">{data.pizza.total}</div>
                <div className="text-[11px] text-textMuted">total</div>
              </div>
            </div>
          </div>
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2 text-sm">
              <span className="h-3 w-3 rounded-full bg-emerald-500/80" />
              <span className="font-semibold text-text">Finalizadas</span>
              <span className="text-emerald-300 text-sm">{data.pizza.finalizadas} ({pctFinal}%)</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <span className="h-3 w-3 rounded-full bg-rose-500/80" />
              <span className="font-semibold text-text">Não realizadas</span>
              <span className="text-rose-300 text-sm">{data.pizza.nao_realizadas} ({pctNao}%)</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
