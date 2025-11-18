"use client";

import { useEffect, useState } from "react";
import { type Agendamento, type AgendamentoLog, getAgendamentoLogs } from "../../lib/api";

type Props = {
  agendamento: Agendamento;
  onClose: () => void;
};

export default function LogsModal({ agendamento, onClose }: Props) {
  const [logs, setLogs] = useState<AgendamentoLog[]>([]);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const response = await getAgendamentoLogs(agendamento.id, page, pageSize);
        if (!cancelled) {
          setLogs(response.items);
          setTotal(response.total);
        }
      } catch (err: any) {
        if (!cancelled) setError(err.message ?? "Erro ao carregar logs.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [agendamento.id, page, pageSize]);

  return (
    <div className="modal-backdrop">
      <div className="modal max-h-[85vh] w-full max-w-3xl overflow-y-auto">
        <div className="modal-header">
          <div>
            <h3>Logs de {agendamento.nome_grupo}</h3>
            <p className="text-sm text-textMuted">Monitoramento de envios</p>
          </div>
          <button type="button" className="secondary" onClick={onClose}>
            Fechar
          </button>
        </div>
        {error && <p className="text-sm text-rose-300">{error}</p>}
        {loading ? (
          <p className="text-sm text-textMuted">Carregando logs...</p>
        ) : (
          <div className="space-y-3">
            {logs.map((log) => (
              <div key={log.id} className="rounded-xl border border-border/60 bg-surface/80 p-3 text-sm">
                <div className="flex items-center justify-between text-xs text-textMuted">
                  <span>{log.data_envio || log.criado_em}</span>
                  <span
                    className={`rounded-full px-2 py-0.5 font-semibold ${
                      log.status === "sucesso"
                        ? "bg-emerald-500/20 text-emerald-200"
                        : "bg-rose-500/20 text-rose-200"
                    }`}
                  >
                    {log.status}
                  </span>
                </div>
                {log.erro && <p className="mt-2 text-rose-300">{log.erro}</p>}
                {log.resposta_api && (
                  <details className="mt-2 text-xs text-textMuted">
                    <summary className="cursor-pointer text-text">Detalhes</summary>
                    <pre className="mt-1 whitespace-pre-wrap rounded bg-surfaceMuted/40 p-2 text-xs text-textMuted">
                      {log.resposta_api}
                    </pre>
                  </details>
                )}
              </div>
            ))}
            {!logs.length && <p className="text-sm text-textMuted">Ainda não há registros.</p>}
          </div>
        )}
        <div className="mt-4 flex items-center justify-between text-xs text-textMuted">
          <span>
            Página {page} de {totalPages}
          </span>
          <div className="space-x-2">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage((prev) => Math.max(1, prev - 1))}
              className="rounded border border-border px-2 py-1 text-text disabled:opacity-40"
            >
              ◀
            </button>
            <button
              type="button"
              disabled={page >= totalPages}
              onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
              className="rounded border border-border px-2 py-1 text-text disabled:opacity-40"
            >
              ▶
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
