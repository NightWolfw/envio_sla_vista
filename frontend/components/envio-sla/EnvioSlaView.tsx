"use client";

import { useEffect, useMemo, useState } from "react";
import {
  type Agendamento,
  type AgendamentoFilters,
  type SlaTemplate,
  cloneAgendamento,
  deleteAgendamento,
  fetchSlaTemplate,
  getAgendamentosPaged,
  pauseAgendamento,
  resumeAgendamento,
  updateSlaTemplate
} from "../../lib/api";
import { templateVariables, tipoEnvioOptions } from "./constants";
import AgendamentoModal from "./AgendamentoModal";
import LogsModal from "./LogsModal";
import TemplateModal from "./TemplateModal";
import ConfirmModal from "./ConfirmModal";

type TemplateState = {
  open: boolean;
  confirm: boolean;
  data: SlaTemplate | null;
  loading: boolean;
  saving: boolean;
  error: string | null;
};

type ModalState = {
  open: boolean;
  mode: "create" | "edit";
  agendamento?: Agendamento | null;
};

type LogsState = {
  open: boolean;
  agendamento?: Agendamento | null;
};

export default function EnvioSlaView() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState({
    grupo: "",
    cr: "",
    tipo_envio: "",
    status: "todos",
    dia: ""
  });
  const [pendingFilters, setPendingFilters] = useState(filters);
  const [agendamentos, setAgendamentos] = useState<Agendamento[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [modal, setModal] = useState<ModalState>({ open: false, mode: "create" });
  const [logsState, setLogsState] = useState<LogsState>({ open: false });
  const [templateState, setTemplateState] = useState<TemplateState>({
    open: false,
    confirm: false,
    data: null,
    loading: false,
    saving: false,
    error: null
  });

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / pageSize)), [total, pageSize]);

  const fetchAgendamentos = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload: AgendamentoFilters = {
        page,
        page_size: pageSize,
        grupo: filters.grupo || undefined,
        cr: filters.cr || undefined,
        tipo_envio: filters.tipo_envio || undefined,
        dia: filters.dia || undefined
      };
      if (filters.status === "ativos") payload.ativo = true;
      if (filters.status === "pausados") payload.ativo = false;
      const response = await getAgendamentosPaged(payload);
      setAgendamentos(response.items);
      setTotal(response.total);
    } catch (err: any) {
      setError(err.message ?? "Erro ao carregar agendamentos.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgendamentos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, filters]);

  const refresh = async (message?: string) => {
    await fetchAgendamentos();
    if (message) {
      setStatusMessage(message);
      setTimeout(() => setStatusMessage(null), 3000);
    }
  };

  const handleApplyFilters = (event: React.FormEvent) => {
    event.preventDefault();
    setFilters(pendingFilters);
    setPage(1);
  };

  const handleResetFilters = () => {
    const clean = { grupo: "", cr: "", tipo_envio: "", status: "todos", dia: "" };
    setPendingFilters(clean);
    setFilters(clean);
    setPage(1);
  };

  const openCreateModal = () => setModal({ open: true, mode: "create" });
  const openEditModal = (agendamento: Agendamento) => setModal({ open: true, mode: "edit", agendamento });
  const closeModal = () => setModal({ open: false, mode: "create", agendamento: undefined });

  const handleDelete = async (agendamento: Agendamento) => {
    if (!confirm(`Remover o agendamento do grupo ${agendamento.nome_grupo}?`)) return;
    try {
      await deleteAgendamento(agendamento.id);
      refresh("Agendamento removido.");
    } catch (err: any) {
      setStatusMessage(err.message ?? "Erro ao remover agendamento.");
    }
  };

  const handleClone = async (agendamento: Agendamento) => {
    try {
      await cloneAgendamento(agendamento.id);
      refresh("Agendamento clonado.");
    } catch (err: any) {
      setStatusMessage(err.message ?? "Erro ao clonar agendamento.");
    }
  };

  const handleToggleStatus = async (agendamento: Agendamento) => {
    try {
      if (agendamento.ativo) {
        await pauseAgendamento(agendamento.id);
        refresh("Agendamento pausado.");
      } else {
        await resumeAgendamento(agendamento.id);
        refresh("Agendamento retomado.");
      }
    } catch (err: any) {
      setStatusMessage(err.message ?? "Erro ao alterar status.");
    }
  };

  const openLogs = (agendamento: Agendamento) => setLogsState({ open: true, agendamento });
  const closeLogs = () => setLogsState({ open: false });

  const openTemplateConfirm = () => setTemplateState((prev) => ({ ...prev, confirm: true }));
  const closeTemplateConfirm = () => setTemplateState((prev) => ({ ...prev, confirm: false }));

  const ensureTemplateLoaded = async () => {
    setTemplateState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const template = await fetchSlaTemplate();
      setTemplateState((prev) => ({ ...prev, data: template }));
    } catch (err: any) {
      setTemplateState((prev) => ({ ...prev, error: err.message ?? "Erro ao carregar template." }));
    } finally {
      setTemplateState((prev) => ({ ...prev, loading: false }));
    }
  };

  const openTemplateModal = async () => {
    closeTemplateConfirm();
    setTemplateState((prev) => ({ ...prev, open: true }));
    if (!templateState.data) {
      await ensureTemplateLoaded();
    }
  };

  const closeTemplateModal = () => setTemplateState((prev) => ({ ...prev, open: false }));

  const handleTemplateSave = async (template: SlaTemplate) => {
    setTemplateState((prev) => ({ ...prev, saving: true, error: null }));
    try {
      const updated = await updateSlaTemplate(template);
      setTemplateState((prev) => ({ ...prev, data: updated }));
      setStatusMessage("Template atualizado com sucesso.");
      closeTemplateModal();
    } catch (err: any) {
      setTemplateState((prev) => ({ ...prev, error: err.message ?? "Erro ao salvar template." }));
    } finally {
      setTemplateState((prev) => ({ ...prev, saving: false }));
    }
  };

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-wide text-textMuted/70">Operações</p>
          <h1 className="text-3xl font-semibold text-white">Envio SLA</h1>
          <p className="text-sm text-textMuted">Gerencie agendamentos, templates e logs de envio.</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={openTemplateConfirm}
            className="rounded-xl border border-border px-4 py-2 text-sm font-medium text-text transition hover:border-accent hover:text-accent"
          >
            Configurações
          </button>
          <button
            type="button"
            onClick={openCreateModal}
            className="rounded-xl bg-accent px-5 py-2 text-sm font-semibold text-slate-900 shadow-panel transition hover:bg-cyan-300"
          >
            Novo Agendamento SLA
          </button>
        </div>
      </header>

      {statusMessage && (
        <div className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-200">
          {statusMessage}
        </div>
      )}

      <section className="rounded-2xl border border-border/80 bg-surface/70 p-4 shadow-panel">
        <button
          type="button"
          onClick={() => setShowFilters((prev) => !prev)}
          className="flex w-full items-center justify-between rounded-xl border border-border px-4 py-2 text-left text-sm text-text transition hover:border-accent"
        >
          <span>Filtro avançado</span>
          <span>{showFilters ? "−" : "+"}</span>
        </button>
        {showFilters && (
          <form className="mt-4 grid gap-3 md:grid-cols-2" onSubmit={handleApplyFilters}>
            <label className="flex flex-col text-sm">
              Grupo
              <input
                className="mt-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text"
                value={pendingFilters.grupo}
                onChange={(e) => setPendingFilters((prev) => ({ ...prev, grupo: e.target.value }))}
              />
            </label>
            <label className="flex flex-col text-sm">
              CR
              <input
                className="mt-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text"
                value={pendingFilters.cr}
                onChange={(e) => setPendingFilters((prev) => ({ ...prev, cr: e.target.value }))}
              />
            </label>
            <label className="flex flex-col text-sm">
              Tipo de envio
              <select
                className="mt-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text"
                value={pendingFilters.tipo_envio}
                onChange={(e) => setPendingFilters((prev) => ({ ...prev, tipo_envio: e.target.value }))}
              >
                <option value="">Todos</option>
                {tipoEnvioOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col text-sm">
              Status
              <select
                className="mt-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text"
                value={pendingFilters.status}
                onChange={(e) => setPendingFilters((prev) => ({ ...prev, status: e.target.value }))}
              >
                <option value="todos">Todos</option>
                <option value="ativos">Ativos</option>
                <option value="pausados">Pausados</option>
              </select>
            </label>
            <label className="flex flex-col text-sm">
              Dia da semana
              <select
                className="mt-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text"
                value={pendingFilters.dia}
                onChange={(e) => setPendingFilters((prev) => ({ ...prev, dia: e.target.value }))}
              >
                <option value="">Todos</option>
                <option value="seg">Seg</option>
                <option value="ter">Ter</option>
                <option value="qua">Qua</option>
                <option value="qui">Qui</option>
                <option value="sex">Sex</option>
                <option value="sab">Sáb</option>
                <option value="dom">Dom</option>
              </select>
            </label>
            <div className="flex items-end gap-3">
              <button
                type="submit"
                className="flex-1 rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-slate-900 shadow hover:bg-cyan-300"
              >
                Aplicar filtros
              </button>
              <button
                type="button"
                onClick={handleResetFilters}
                className="rounded-xl border border-border px-4 py-2 text-sm text-text hover:text-accent"
              >
                Limpar
              </button>
            </div>
          </form>
        )}
      </section>

      <section className="rounded-2xl border border-border/70 bg-surface/80 p-4 shadow-panel">
        {error && (
          <p className="mb-4 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">
            {error}
          </p>
        )}
        {loading ? (
          <div className="animate-pulse rounded-xl border border-border/60 bg-surfaceMuted/40 p-6 text-center text-textMuted">
            Carregando agendamentos...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px] border-collapse text-sm text-text">
              <thead className="bg-surfaceMuted/60 text-xs uppercase tracking-wide text-textMuted">
                <tr>
                  <th className="px-3 py-2 text-left">Grupo</th>
                  <th className="px-3 py-2 text-left">CR</th>
                  <th className="px-3 py-2 text-left">Tipo</th>
                  <th className="px-3 py-2 text-left">Dias</th>
                  <th className="px-3 py-2 text-left">Janela</th>
                  <th className="px-3 py-2 text-left">Próximo envio</th>
                  <th className="px-3 py-2 text-left">Status</th>
                  <th className="px-3 py-2 text-left">Último envio</th>
                  <th className="px-3 py-2 text-center">Ações</th>
                </tr>
              </thead>
              <tbody>
                {agendamentos.map((item) => (
                  <tr key={item.id} className="border-b border-border/40 text-sm">
                    <td className="px-3 py-2 font-medium text-white">{item.nome_grupo}</td>
                    <td className="px-3 py-2 text-textMuted">{item.cr ?? "--"}</td>
                    <td className="px-3 py-2 capitalize">{item.tipo_envio}</td>
                    <td className="px-3 py-2 text-textMuted">
                      {item.dias_semana ? item.dias_semana.split(",").map((d) => d.trim()).join(", ") : "--"}
                    </td>
                    <td className="px-3 py-2 text-textMuted">
                      {item.hora_inicio?.slice(0, 5)} / {item.hora_fim?.slice(0, 5)}
                    </td>
                    <td className="px-3 py-2 text-textMuted">{item.proximo_envio ?? "--"}</td>
                    <td className="px-3 py-2">
                      <span
                        className={`rounded-full px-2 py-1 text-xs font-semibold ${
                          item.ativo ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-200"
                        }`}
                      >
                        {item.ativo ? "Ativo" : "Pausado"}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-textMuted">
                      {item.ultimo_status ? (
                        <span>
                          {item.ultimo_status}{" "}
                          {item.ultimo_envio && <span className="text-xs text-textMuted/70">({item.ultimo_envio})</span>}
                        </span>
                      ) : (
                        "--"
                      )}
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex items-center justify-center gap-2 text-xs">
                        <button className="text-accent hover:underline" onClick={() => openEditModal(item)}>
                          Editar
                        </button>
                        <button className="text-accent hover:underline" onClick={() => handleClone(item)}>
                          Clonar
                        </button>
                        <button className="text-accent hover:underline" onClick={() => handleToggleStatus(item)}>
                          {item.ativo ? "Pausar" : "Retomar"}
                        </button>
                        <button className="text-accent hover:underline" onClick={() => openLogs(item)}>
                          Logs
                        </button>
                        <button className="text-rose-300 hover:underline" onClick={() => handleDelete(item)}>
                          Excluir
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {!agendamentos.length && !loading && (
                  <tr>
                    <td className="px-3 py-6 text-center text-textMuted" colSpan={9}>
                      Nenhum agendamento encontrado com os filtros atuais.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-textMuted">
        <div>
          Página {page} de {totalPages} • {total} registros
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => setPage((prev) => Math.max(1, prev - 1))}
            className="rounded-lg border border-border px-3 py-1 text-text disabled:opacity-40"
          >
            Anterior
          </button>
          <button
            type="button"
            disabled={page >= totalPages}
            onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
            className="rounded-lg border border-border px-3 py-1 text-text disabled:opacity-40"
          >
            Próxima
          </button>
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setPage(1);
            }}
            className="rounded-lg border border-border bg-surface px-2 py-1 text-text"
          >
            {[10, 20, 50].map((size) => (
              <option key={size} value={size}>
                {size}/página
              </option>
            ))}
          </select>
        </div>
      </div>

      {modal.open && (
        <AgendamentoModal
          mode={modal.mode}
          agendamento={modal.agendamento ?? undefined}
          onClose={closeModal}
          onSaved={(message) => {
            closeModal();
            refresh(message);
          }}
        />
      )}

      {logsState.open && logsState.agendamento && (
        <LogsModal agendamento={logsState.agendamento} onClose={closeLogs} />
      )}

      {templateState.confirm && (
        <ConfirmModal
          title="Alterar template?"
          description="Atualizar o template afetará todos os agendamentos já existentes. Deseja continuar?"
          confirmLabel="Sim, editar template"
          cancelLabel="Cancelar"
          onConfirm={openTemplateModal}
          onCancel={closeTemplateConfirm}
        />
      )}

      {templateState.open && (
        <TemplateModal
          template={templateState.data}
          loading={templateState.loading}
          saving={templateState.saving}
          error={templateState.error}
          variables={templateVariables}
          onRetry={ensureTemplateLoaded}
          onClose={closeTemplateModal}
          onSave={handleTemplateSave}
        />
      )}
    </div>
  );
}
