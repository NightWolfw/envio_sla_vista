"use client";

import { useEffect, useState } from "react";
import type { SlaTemplate } from "../../lib/api";
type Props = {
  template: SlaTemplate | null;
  loading: boolean;
  saving: boolean;
  error: string | null;
  variables: string[];
  onRetry: () => void;
  onClose: () => void;
  onSave: (template: SlaTemplate) => Promise<void>;
};

export default function TemplateModal({ template, loading, saving, error, variables, onRetry, onClose, onSave }: Props) {
  const [localTemplate, setLocalTemplate] = useState<SlaTemplate>(
    template ?? { resultados: "", programadas: "" }
  );

  useEffect(() => {
    if (template) setLocalTemplate(template);
  }, [template]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await onSave(localTemplate);
  };

  return (
    <div className="modal-backdrop">
      <div className="modal max-h-[90vh] w-full max-w-4xl overflow-y-auto">
        <div className="modal-header">
          <h3>Editar template SLA</h3>
          <button type="button" className="secondary" onClick={onClose}>
            Fechar
          </button>
        </div>
        {loading ? (
          <p className="text-sm text-textMuted">Carregando template...</p>
        ) : error ? (
          <div className="space-y-3 text-sm">
            <p className="text-rose-300">{error}</p>
            <button className="rounded-xl border border-border px-4 py-2 text-text" onClick={onRetry}>
              Tentar novamente
            </button>
          </div>
        ) : (
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="flex items-center gap-2 text-sm text-textMuted">
              <span role="img" aria-label="info" title={`Variáveis: ${variables.join(", ")}`}>
                ℹ️
              </span>
              Variáveis permitidas: {variables.join(", ")}
            </div>
            <label className="text-sm font-semibold text-text">
              Template - Resultados
              <textarea
                className="mt-1 w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-text"
                rows={8}
                value={localTemplate.resultados}
                onChange={(e) => setLocalTemplate((prev) => ({ ...prev, resultados: e.target.value }))}
              />
            </label>
            <label className="text-sm font-semibold text-text">
              Template - Programadas
              <textarea
                className="mt-1 w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-text"
                rows={8}
                value={localTemplate.programadas}
                onChange={(e) => setLocalTemplate((prev) => ({ ...prev, programadas: e.target.value }))}
              />
            </label>
            <div className="flex justify-end gap-3">
              <button type="button" className="secondary" onClick={onClose}>
                Cancelar
              </button>
              <button
                type="submit"
                disabled={saving}
                className="rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-slate-900"
              >
                {saving ? "Salvando..." : "Salvar template"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
