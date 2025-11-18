"use client";

import { useState } from "react";
import type { Grupo } from "../lib/api";
import { clientApi } from "../lib/client";
import { useRouter } from "next/navigation";

type Props = {
  grupo: Grupo;
  onClose: () => void;
};

const inputClasses =
  "block w-full rounded-xl border border-border bg-surface/70 px-3 py-2 text-sm text-text placeholder:text-textMuted focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/50 transition";

export default function EditGroupModal({ grupo, onClose }: Props) {
  const router = useRouter();
  const [status, setStatus] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setStatus(null);
    const form = new FormData(event.currentTarget);
    try {
      await clientApi.put(`/grupos/${grupo.id}`, {
        group_id: form.get("group_id"),
        nome: form.get("nome_grupo"),
        enviar_mensagem: form.get("envio") === "on",
        cr: form.get("cr")
      });
      setStatus({ type: "success", message: "Grupo atualizado com sucesso!" });
      router.refresh();
      setTimeout(onClose, 1200);
    } catch (error: any) {
      setStatus({ type: "error", message: error.message ?? "Erro ao atualizar o grupo." });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm">
      <div className="w-full max-w-2xl rounded-2xl border border-border bg-surface p-6 shadow-panel">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-wide text-textMuted/70">Editar grupo</p>
            <h3 className="text-xl font-semibold text-white">{grupo.nome_grupo}</h3>
          </div>
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-xl border border-border/60 px-4 py-2 text-sm font-medium text-text transition hover:border-accent hover:text-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            onClick={onClose}
          >
            Fechar
          </button>
        </div>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="flex flex-col gap-2 text-sm font-semibold text-text">
              Group ID
              <input className={inputClasses} name="group_id" defaultValue={grupo.group_id} required />
            </label>
            <label className="flex flex-col gap-2 text-sm font-semibold text-text">
              Nome
              <input className={inputClasses} name="nome_grupo" defaultValue={grupo.nome_grupo} required />
            </label>
            <label className="flex flex-col gap-2 text-sm font-semibold text-text md:col-span-2">
              CR
              <input className={inputClasses} name="cr" defaultValue={grupo.cr ?? ""} />
            </label>
          </div>
          <label className="flex items-center gap-3 text-sm font-medium text-text">
            <input
              type="checkbox"
              name="envio"
              defaultChecked={grupo.envio}
              className="h-5 w-5 rounded border-border bg-surface accent-accent transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            />
            <span>Habilitar envio</span>
          </label>
          <div className="flex items-center justify-end gap-3">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center justify-center rounded-xl bg-accent px-5 py-2 text-sm font-semibold text-slate-900 shadow-sm transition hover:bg-cyan-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-70"
            >
              {loading ? "Salvando..." : "Salvar alterações"}
            </button>
          </div>
        </form>
        {status && (
          <p
            className={`mt-3 text-sm ${
              status.type === "success" ? "text-emerald-400" : "text-rose-400"
            }`}
          >
            {status.message}
          </p>
        )}
      </div>
    </div>
  );
}
