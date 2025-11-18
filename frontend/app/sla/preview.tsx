"use client";

import { useState } from "react";
import type { Grupo } from "../../lib/api";
import { clientApi } from "../../lib/client";

type Props = {
  grupos: Grupo[];
};

type PreviewResponse = {
  grupo_nome: string;
  mensagem: string;
  stats: Record<string, number>;
};

export default function SlaPreviewClient({ grupos }: Props) {
  const [resultado, setResultado] = useState<PreviewResponse | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const grupoId = Number(form.get("grupo_id"));
    try {
      const resposta = await clientApi.post<PreviewResponse>(`/sla/preview/${grupoId}`, {
        tipo_envio: form.get("tipo_envio"),
        data_envio: form.get("data_envio"),
        hora_inicio: form.get("hora_inicio"),
        dia_offset_inicio: Number(form.get("dia_offset_inicio") ?? 0),
        hora_fim: form.get("hora_fim"),
        dia_offset_fim: Number(form.get("dia_offset_fim") ?? 0)
      });
      setResultado(resposta);
      setErro(null);
    } catch (error: any) {
      setErro(error.message ?? "Erro ao gerar preview");
      setResultado(null);
    }
  }

  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <form onSubmit={handleSubmit} className="grid" style={{ gap: "0.75rem" }}>
        <label>
          Grupo
          <select name="grupo_id" required defaultValue="">
            <option value="" disabled>
              Selecione
            </option>
            {grupos
              .filter((g) => !!g.cr)
              .map((grupo) => (
                <option key={grupo.id} value={grupo.id}>
                  {grupo.nome_grupo} ({grupo.cr})
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
          Data de envio
          <input type="datetime-local" name="data_envio" required />
        </label>
        <label>
          Hora início
          <input type="time" name="hora_inicio" required />
        </label>
        <label>
          Offset início (dias)
          <input type="number" name="dia_offset_inicio" defaultValue={0} />
        </label>
        <label>
          Hora fim
          <input type="time" name="hora_fim" required />
        </label>
        <label>
          Offset fim (dias)
          <input type="number" name="dia_offset_fim" defaultValue={0} />
        </label>
        <button type="submit">Gerar preview</button>
      </form>

      {erro && <p>{erro}</p>}
      {resultado && (
        <div className="panel">
          <h3>Mensagem gerada ({resultado.grupo_nome})</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>{resultado.mensagem}</pre>
          <h4>Indicadores</h4>
          <ul>
            {Object.entries(resultado.stats).map(([key, value]) => (
              <li key={key}>
                {key}: {value}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
