"use client";

import { useState } from "react";
import type { Agendamento, Grupo } from "../../lib/api";
import { clientApi } from "../../lib/client";

type Props = {
  agendamentos: Agendamento[];
  grupos: Grupo[];
};

export default function AgendamentosClient({ agendamentos, grupos }: Props) {
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const dias = (data.get("dias_semana") as string)
      .split(",")
      .map((d) => d.trim())
      .filter(Boolean);
    try {
      await clientApi.post("/agendamentos", {
        grupo_id: Number(data.get("grupo_id")),
        tipo_envio: data.get("tipo_envio"),
        dias_semana: dias,
        data_envio: data.get("data_envio"),
        hora_inicio: data.get("hora_inicio"),
        dia_offset_inicio: Number(data.get("dia_offset_inicio") ?? 0),
        hora_fim: data.get("hora_fim"),
        dia_offset_fim: Number(data.get("dia_offset_fim") ?? 0)
      });
      setMessage("Agendamento criado! Recarregue para visualizar.");
      event.currentTarget.reset();
    } catch (err: any) {
      setMessage(err.message ?? "Erro ao criar agendamento");
    }
  }

  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <div style={{ overflowX: "auto" }}>
        <table>
          <thead>
            <tr>
              <th>Grupo</th>
              <th>CR</th>
              <th>Tipo</th>
              <th>Dias</th>
              <th>Horário</th>
              <th>Ativo</th>
            </tr>
          </thead>
          <tbody>
            {agendamentos.map((agendamento) => (
              <tr key={agendamento.id}>
                <td>{agendamento.nome_grupo}</td>
                <td>{agendamento.cr ?? "—"}</td>
                <td>{agendamento.tipo_envio}</td>
                <td>{agendamento.dias_semana ?? "—"}</td>
                <td>
                  {agendamento.hora_inicio} → {agendamento.hora_fim}
                </td>
                <td>{agendamento.ativo ? "Sim" : "Não"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <form className="panel" onSubmit={handleSubmit}>
        <h3>Novo agendamento</h3>
        <div className="grid" style={{ gap: "0.75rem" }}>
          <label>
            Grupo
            <select name="grupo_id" required defaultValue="">
              <option value="" disabled>
                Selecione
              </option>
              {grupos.map((grupo) => (
                <option key={grupo.id} value={grupo.id}>
                  {grupo.nome_grupo}
                </option>
              ))}
            </select>
          </label>
          <label>
            Tipo de envio
            <select name="tipo_envio" defaultValue="resultados">
              <option value="resultados">Resultados</option>
              <option value="programadas">Programadas</option>
            </select>
          </label>
          <label>
            Dias da semana (seg,ter,...)
            <input name="dias_semana" placeholder="seg,ter,qua" defaultValue="seg,ter,qua,qui,sex" />
          </label>
          <label>
            Data de envio
            <input type="datetime-local" name="data_envio" required />
          </label>
          <label>
            Hora início
            <input type="time" name="hora_inicio" required />
          </label>
          <label>
            Hora fim
            <input type="time" name="hora_fim" required />
          </label>
          <label>
            Offset início (dias)
            <input type="number" name="dia_offset_inicio" defaultValue={0} />
          </label>
          <label>
            Offset fim (dias)
            <input type="number" name="dia_offset_fim" defaultValue={0} />
          </label>
          <button type="submit">Criar agendamento</button>
        </div>
        {message && <p style={{ marginTop: "0.75rem" }}>{message}</p>}
      </form>
    </div>
  );
}
