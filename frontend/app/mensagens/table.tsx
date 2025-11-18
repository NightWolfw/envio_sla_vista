"use client";

import { useState } from "react";
import type { Grupo, Mensagem } from "../../lib/api";
import { clientApi } from "../../lib/client";

type Props = {
  mensagens: Mensagem[];
  grupos: Grupo[];
};

export default function MensagensClient({ mensagens, grupos }: Props) {
  const [feedback, setFeedback] = useState<string | null>(null);

  async function handleCreate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const gruposSelec = form.getAll("grupos") as string[];
    const dias = form
      .getAll("dias_semana")
      .map((value) => Number(value))
      .filter((n) => !Number.isNaN(n));

    try {
      await clientApi.post("/mensagens", {
        mensagem: form.get("mensagem"),
        grupos_ids: gruposSelec,
        tipo_recorrencia: form.get("tipo_recorrencia"),
        dias_semana: dias.length ? dias : null,
        horario: form.get("horario"),
        data_inicio: form.get("data_inicio"),
        data_fim: form.get("data_fim") || null
      });
      event.currentTarget.reset();
      setFeedback("Mensagem criada! Recarregue para visualizar.");
    } catch (error: any) {
      setFeedback(error.message ?? "Erro ao criar mensagem");
    }
  }

  async function toggleMensagem(id: number) {
    try {
      await clientApi.post(`/mensagens/${id}/toggle`);
      setFeedback("Status alterado! Atualize para ver o resultado.");
    } catch (error: any) {
      setFeedback(error.message ?? "Erro ao alternar status");
    }
  }

  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <div style={{ overflowX: "auto" }}>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Mensagem</th>
              <th>Tipo</th>
              <th>Dias</th>
              <th>Horário</th>
              <th>Ativo</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {mensagens.map((mensagem) => (
              <tr key={mensagem.id}>
                <td>{mensagem.id}</td>
                <td>{mensagem.mensagem.slice(0, 50)}...</td>
                <td>{mensagem.tipo_recorrencia}</td>
                <td>{mensagem.dias_semana?.join(", ") ?? "—"}</td>
                <td>{mensagem.horario}</td>
                <td>{mensagem.ativo ? "Sim" : "Não"}</td>
                <td>
                  <button type="button" onClick={() => toggleMensagem(mensagem.id)}>
                    Alternar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <form className="panel" onSubmit={handleCreate}>
        <h3>Criar nova mensagem</h3>
        <div className="grid" style={{ gap: "0.75rem" }}>
          <label>
            Mensagem
            <textarea name="mensagem" required rows={4} />
          </label>
          <label>
            Grupos
            <select name="grupos" multiple required size={5}>
              {grupos.map((grupo) => (
                <option key={grupo.id} value={grupo.group_id}>
                  {grupo.nome_grupo}
                </option>
              ))}
            </select>
          </label>
          <label>
            Tipo
            <select name="tipo_recorrencia" defaultValue="UNICA">
              <option value="UNICA">Única</option>
              <option value="RECORRENTE">Recorrente</option>
            </select>
          </label>
          <label>
            Dias semana (0=Dom ... 6=Sáb)
            <input name="dias_semana" placeholder="0,1,2" />
          </label>
          <label>
            Horário
            <input type="time" name="horario" required />
          </label>
          <label>
            Data início
            <input type="date" name="data_inicio" required />
          </label>
          <label>
            Data fim (opcional)
            <input type="date" name="data_fim" />
          </label>
          <button type="submit">Salvar mensagem</button>
        </div>
        {feedback && <p style={{ marginTop: "0.75rem" }}>{feedback}</p>}
      </form>
    </div>
  );
}
