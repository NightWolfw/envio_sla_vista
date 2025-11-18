"use client";

import { useState } from "react";
import type { EnvioGrupo } from "../../lib/api";
import { clientApi } from "../../lib/client";

type Props = {
  grupos: EnvioGrupo[];
};

type EnvioResposta = {
  sucessos: number;
  erros: number;
  detalhes: Array<{
    grupo: string;
    group_id: string;
    sucesso: boolean;
    erro?: string | null;
  }>;
};

export default function EnvioForm({ grupos }: Props) {
  const [status, setStatus] = useState<string | null>(null);
  const [detalhes, setDetalhes] = useState<EnvioResposta["detalhes"] | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const mensagem = form.get("mensagem") as string;
    const gruposSelecionados = form.getAll("grupos") as string[];

    if (!mensagem.trim() || !gruposSelecionados.length) {
      setStatus("Preencha a mensagem e selecione pelo menos um grupo.");
      return;
    }

    setLoading(true);
    setStatus(null);
    setDetalhes(null);

    try {
      const resposta = await clientApi.post<EnvioResposta>("/envio/processar", {
        mensagem,
        grupos_ids: gruposSelecionados
      });
      setStatus(
        `Envios concluídos: ${resposta.sucessos} sucesso(s), ${resposta.erros} erro(s).`
      );
      setDetalhes(resposta.detalhes);
      event.currentTarget.reset();
    } catch (error: any) {
      setStatus(error.message ?? "Falha ao enviar mensagens");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="grid" style={{ gap: "1rem" }} onSubmit={handleSubmit}>
      <label>
        Mensagem
        <textarea name="mensagem" rows={5} required placeholder="Digite a mensagem a enviar" />
      </label>

      <label>
        Grupos (segure Ctrl/Cmd para selecionar múltiplos)
        <select name="grupos" multiple required size={Math.min(grupos.length, 10)}>
          {grupos.map((grupo) => (
            <option key={grupo.group_id} value={grupo.group_id}>
              {grupo.nome_grupo} ({grupo.group_id})
            </option>
          ))}
        </select>
      </label>

      <button type="submit" disabled={loading}>
        {loading ? "Enviando..." : "Enviar mensagem"}
      </button>

      {status && <p style={{ margin: 0 }}>{status}</p>}

      {detalhes && (
        <div className="panel" style={{ marginTop: "1rem" }}>
          <h3>Detalhes</h3>
          <table>
            <thead>
              <tr>
                <th>Grupo</th>
                <th>ID</th>
                <th>Status</th>
                <th>Erro</th>
              </tr>
            </thead>
            <tbody>
              {detalhes.map((item) => (
                <tr key={item.group_id}>
                  <td>{item.grupo}</td>
                  <td>{item.group_id}</td>
                  <td>{item.sucesso ? "SUCESSO" : "ERRO"}</td>
                  <td>{item.erro ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </form>
  );
}
