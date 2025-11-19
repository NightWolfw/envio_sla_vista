"use client";

export default function EnvioWhatsView() {
  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-wide text-textMuted/70">Operações</p>
          <h1 className="text-2xl font-semibold text-white">Envio Whats</h1>
          <p className="text-sm text-textMuted">Dispare mensagens rápidas ou agende envios personalizados.</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="rounded-xl bg-surfaceMuted/50 px-4 py-2 text-sm font-medium text-text hover:text-accent"
          >
            Envio rápido
          </button>
          <button
            type="button"
            className="rounded-xl border border-border px-4 py-2 text-sm font-medium text-text transition hover:border-accent hover:text-accent"
          >
            Novo agendamento
          </button>
        </div>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-border bg-surface/80 p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-white">Envio rápido</h2>
          <p className="text-sm text-textMuted">Selecione grupos e envie mensagens personalizadas instantaneamente.</p>
          <div className="mt-4 space-y-3 text-sm">
            <label className="flex flex-col">
              Selecionar grupos
              <input
                disabled
                placeholder="Integração em desenvolvimento"
                className="mt-1 rounded-lg border border-border bg-surface px-3 py-2 text-textMuted"
              />
            </label>
            <label className="flex flex-col">
              Mensagem
              <textarea
                disabled
                placeholder="Digite aqui a mensagem a ser enviada"
                className="mt-1 h-28 rounded-lg border border-border bg-surface px-3 py-2 text-textMuted"
              />
            </label>
            <button type="button" disabled className="w-full rounded-xl bg-accent/40 px-4 py-2 text-sm font-semibold text-slate-900/70">
              Enviar agora
            </button>
          </div>
        </div>
        <div className="rounded-2xl border border-border bg-surface/80 p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-white">Agendados</h2>
          <p className="text-sm text-textMuted">
            Em breve: acompanhe seus agendamentos de WhatsApp com filtros, logs e edição.
          </p>
          <div className="mt-4 rounded-xl border border-border/60 bg-surfaceMuted/30 p-4 text-sm text-textMuted">
            Tabela e controles avançados serão disponibilizados após integração com backend de mensagens.
          </div>
        </div>
      </section>
    </div>
  );
}
