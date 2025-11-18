"use client";

import { useEffect, useMemo, useState } from "react";
import type { Grupo } from "../lib/api";
import { FaEdit } from "react-icons/fa";

type Props = {
  grupos: Grupo[];
  selectedIds: number[];
  onToggle: (id: number) => void;
  onToggleAll: (ids: number[]) => void;
  onEdit: (grupo: Grupo) => void;
};

const PAGE_SIZE = 10;

export default function GroupTable({ grupos, selectedIds, onToggle, onToggleAll, onEdit }: Props) {
  const [page, setPage] = useState(1);

  useEffect(() => {
    setPage(1);
  }, [grupos.length]);

  const data = useMemo(() => {
    const totalPages = Math.max(1, Math.ceil(grupos.length / PAGE_SIZE));
    const currentPage = Math.min(page, totalPages);
    const start = (currentPage - 1) * PAGE_SIZE;
    const current = grupos.slice(start, start + PAGE_SIZE);
    return {
      totalPages,
      currentPage,
      items: current,
    };
  }, [grupos, page]);

  const visibleIds = data.items.map((g) => g.id);
  const allSelected = visibleIds.length > 0 && visibleIds.every((id) => selectedIds.includes(id));

  return (
    <div style={{ display: "grid", gap: "1rem" }}>
      <div style={{ overflowX: "auto" }}>
        <table>
          <thead>
            <tr>
              <th>
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={() => onToggleAll(visibleIds)}
                />
              </th>
              <th>Nome</th>
              <th>Group ID</th>
              <th>CR</th>
              <th>Envio</th>
              <th>Cliente</th>
              <th>PEC 01</th>
              <th>PEC 02</th>
              <th>Diretor Executivo</th>
              <th>Diretor Regional</th>
              <th>Gerente Regional</th>
              <th>Gerente</th>
              <th>Supervisor</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((grupo) => {
              const checked = selectedIds.includes(grupo.id);
              return (
                <tr key={grupo.id}>
                  <td>
                    <input type="checkbox" checked={checked} onChange={() => onToggle(grupo.id)} />
                  </td>
                  <td>{grupo.nome_grupo}</td>
                  <td>{grupo.group_id}</td>
                  <td>{grupo.cr ?? "—"}</td>
                  <td>
                    <span className="chip">{grupo.envio ? "Ativo" : "Inativo"}</span>
                  </td>
                  <td>{grupo.cliente ?? "—"}</td>
                  <td>{grupo.pec_01 ?? "—"}</td>
                  <td>{grupo.pec_02 ?? "—"}</td>
                  <td>{grupo.diretor_executivo ?? "—"}</td>
                  <td>{grupo.diretor_regional ?? "—"}</td>
                  <td>{grupo.gerente_regional ?? "—"}</td>
                  <td>{grupo.gerente ?? "—"}</td>
                  <td>{grupo.supervisor ?? "—"}</td>
                  <td>
                    <button type="button" className="secondary" onClick={() => onEdit(grupo)}>
                      <FaEdit style={{ marginRight: "0.35rem" }} />
                      Editar
                    </button>
                  </td>
                </tr>
              );
            })}
            {data.items.length === 0 && (
              <tr>
                <td colSpan={14} style={{ textAlign: "center", padding: "1rem" }}>
                  Nenhum grupo encontrado com os filtros atuais.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span>
          Página {data.currentPage} de {data.totalPages} — {grupos.length} grupo(s)
        </span>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button
            type="button"
            className="secondary"
            disabled={data.currentPage === 1}
            onClick={() => setPage((prev) => Math.max(1, prev - 1))}
          >
            ◀
          </button>
          <button
            type="button"
            className="secondary"
            disabled={data.currentPage === data.totalPages}
            onClick={() => setPage((prev) => Math.min(data.totalPages, prev + 1))}
          >
            ▶
          </button>
        </div>
      </div>
    </div>
  );
}
