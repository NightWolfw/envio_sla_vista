"use client";

import { useEffect, useState } from "react";
import {
  type Agendamento,
  type AgendamentoPayload,
  type Grupo,
  createAgendamento,
  getGrupos,
  updateAgendamento
} from "../../lib/api";
import { tipoEnvioOptions, weekdayOptions } from "./constants";

type Props = {
  mode: "create" | "edit";
  agendamento?: Agendamento;
  onClose: () => void;
  onSaved: (message: string) => void;
};

export default function AgendamentoModal({ mode, agendamento, onClose, onSaved }: Props) {
  const [grupos, setGrupos] = useState<Grupo[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<AgendamentoPayload>(() => {
    if (!agendamento) {
      return {
        grupo_id: 0,
        tipo_envio: "resultados",
        dias_semana: [],
        data_envio: "",
        hora_inicio: "08:00",
        dia_offset_inicio: 0,
        hora_fim: "18:00",
        dia_offset_fim: 0
      };
    }
    return {
      grupo_id: agendamento.grupo_id,
      tipo_envio: agendamento.tipo_envio as "resultados" | "programadas",
      dias_semana: agendamento.dias_semana
        ? agendamento.dias_semana.split(",").map((d) => d.trim()).filter(Boolean)
        : [],
      data_envio: toDateInput(agendamento.data_envio),
      hora_inicio: agendamento.hora_inicio?.slice(0, 5) ?? "08:00",
      dia_offset_inicio: agendamento.dia_offset_inicio ?? 0,
      hora_fim: agendamento.hora_fim?.slice(0, 5) ?? "18:00",
      dia_offset_fim: agendamento.dia_offset_fim ?? 0
    };
  });

  useEffect(() => {
    async function load() {
      try {
        const data = await getGrupos();
        setGrupos(data);
      } catch (err: any) {
        setError(err.message ?? "Erro ao carregar grupos disponíveis.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.grupo_id) {
      setError("Selecione um grupo.");
      return;
    }
    if (!form.data_envio) {
      setError("Informe a primeira data de envio.");
      return;
    }
    setSaving(true);
    setError(null);
    const payload: AgendamentoPayload = {
      ...form,
      data_envio: new Date(form.data_envio).toISOString(),
      hora_inicio: normalizeTime(form.hora_inicio),
      hora_fim: normalizeTime(form.hora_fim)
    };
    try {
      if (mode === "edit" && agendamento) {
        await updateAgendamento(agendamento.id, payload);
        onSaved("Agendamento atualizado.");
      } else {
        await createAgendamento(payload);
        onSaved("Agendamento criado.");
      }
    } catch (err: any) {
      setError(err.message ?? "Erro ao salvar agendamento.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal max-h-[90vh] w-full max-w-3xl overflow-y-auto">
        <div className="modal-header">
          <h3>{mode === "create" ? "Novo agendamento SLA" : `Editar ${agendamento?.nome_grupo}`}</h3>
          <button type="button" className="secondary" onClick={onClose}>
            Fechar
          </button>
        </div>
        {loading ? (
          <p className="text-sm text-textMuted">Carregando grupos...</p>
        ) : (
          <form className="grid gap-4" onSubmit={handleSubmit}>
            <label className="text-sm font-semibold">
              Grupo
              <select
                className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text"
                value={form.grupo_id || ""}
                onChange={(e) => setForm((prev) => ({ ...prev, grupo_id: Number(e.target.value) }))}
                required
              >
                <option value="">Selecione o grupo</option>
                {grupos.map((grupo) => (
                  <option key={grupo.id} value={grupo.id}>
                    {grupo.nome_grupo}
                  </option>
                ))}
              </select>
            </label>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="text-sm font-semibold">
                Tipo de envio
                <select
                  className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text"
                  value={form.tipo_envio}
                  onChange={(e) => setForm((prev) => ({ ...prev, tipo_envio: e.target.value as "resultados" | "programadas" }))}
                >
                  {tipoEnvioOptions.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-sm font-semibold">
                Primeira execução
                <input
                  type="datetime-local"
                  className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text"
                  value={form.data_envio}
                  onChange={(e) => setForm((prev) => ({ ...prev, data_envio: e.target.value }))}
                  required
                />
              </label>
            </div>
            <fieldset className="rounded-xl border border-border/60 p-3">
              <legend className="px-2 text-sm font-semibold text-text">Dias da semana</legend>
              <div className="flex flex-wrap gap-3 text-sm">
                {weekdayOptions.map((opt) => {
                  const checked = form.dias_semana.includes(opt.value);
                  return (
                    <label key={opt.value} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={(e) => {
                          setForm((prev) => {
                            const dias = new Set(prev.dias_semana);
                            if (e.target.checked) dias.add(opt.value);
                            else dias.delete(opt.value);
                            return { ...prev, dias_semana: Array.from(dias) };
                          });
                        }}
                      />
                      {opt.label}
                    </label>
                  );
                })}
              </div>
            </fieldset>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="text-sm font-semibold">
                Hora inicial
                <input
                  type="time"
                  className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text"
                  value={form.hora_inicio}
                  onChange={(e) => setForm((prev) => ({ ...prev, hora_inicio: e.target.value }))}
                />
              </label>
              <label className="text-sm font-semibold">
                Offset início (dias)
                <input
                  type="number"
                  className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text"
                  value={form.dia_offset_inicio}
                  onChange={(e) => setForm((prev) => ({ ...prev, dia_offset_inicio: Number(e.target.value) }))}
                />
              </label>
              <label className="text-sm font-semibold">
                Hora final
                <input
                  type="time"
                  className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text"
                  value={form.hora_fim}
                  onChange={(e) => setForm((prev) => ({ ...prev, hora_fim: e.target.value }))}
                />
              </label>
              <label className="text-sm font-semibold">
                Offset fim (dias)
                <input
                  type="number"
                  className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text"
                  value={form.dia_offset_fim}
                  onChange={(e) => setForm((prev) => ({ ...prev, dia_offset_fim: Number(e.target.value) }))}
                />
              </label>
            </div>
            {error && <p className="text-sm text-rose-300">{error}</p>}
            <div className="flex justify-end gap-3">
              <button type="button" className="secondary" onClick={onClose}>
                Cancelar
              </button>
              <button type="submit" disabled={saving} className="rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-slate-900">
                {saving ? "Salvando..." : "Salvar"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

function toDateInput(value: string | null | undefined) {
  if (!value) return "";
  const date = new Date(value);
  return date.toISOString().slice(0, 16);
}

function normalizeTime(value: string) {
  if (!value) return "00:00";
  return value.length === 5 ? `${value}:00` : value;
}
