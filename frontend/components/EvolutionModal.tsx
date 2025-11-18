"use client";

import { useEffect, useMemo, useState } from "react";
import { getEvolutionGroups, type EvolutionGroup, importEvolutionGroups } from "../lib/api";
import { useRouter } from "next/navigation";

type Props = {
  onClose: () => void;
};

type SelectState = {
  [group_id: string]: {
    selected: boolean;
    cr: string;
  };
};

export default function EvolutionModal({ onClose }: Props) {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [pageSize] = useState(25);
  const [total, setTotal] = useState(0);
  const [items, setItems] = useState<EvolutionGroup[]>([]);
  const [state, setState] = useState<SelectState>({});
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<string | null>(null);
  const [importProgress, setImportProgress] = useState(0);
  const [importTotal, setImportTotal] = useState(0);
  const [importing, setImporting] = useState(false);
  const [loadProgress, setLoadProgress] = useState(0);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoadProgress(5);
      setLoading(true);
      try {
        const interval = setInterval(() => {
          setLoadProgress((prev) => Math.min(prev + 10, 90));
        }, 150);
        const data = await getEvolutionGroups(page, pageSize);
        clearInterval(interval);
        if (!cancelled) {
          setItems(data.grupos);
          setTotal(data.total);
          setState({});
          setLoadProgress(100);
        }
      } catch (error: any) {
        if (!cancelled) setStatus(error.message ?? "Erro ao carregar grupos da Evolution.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [page, pageSize]);

  const filtered = useMemo(() => {
    const text = search.toLowerCase().trim();
    if (!text) return items;
    return items.filter((grupo) => grupo.nome.toLowerCase().includes(text));
  }, [items, search]);

  function toggleSelect(group: EvolutionGroup) {
    setState((prev) => ({
      ...prev,
      [group.group_id]: {
        selected: !prev[group.group_id]?.selected,
        cr: prev[group.group_id]?.cr ?? ""
      }
    }));
  }

  function updateCr(group_id: string, cr: string) {
    setState((prev) => ({
      ...prev,
      [group_id]: {
        selected: prev[group_id]?.selected ?? false,
        cr
      }
    }));
  }

  async function handleImport() {
    const selecionados = Object.entries(state)
      .filter(([, info]) => info.selected)
      .map(([group_id, info]) => ({
        group_id,
        nome: items.find((i) => i.group_id === group_id)?.nome ?? "",
        cr: info.cr || null
      }));

    if (!selecionados.length) {
      setStatus("Selecione pelo menos um grupo.");
      return;
    }

    try {
      setImporting(true);
      setImportTotal(selecionados.length);
      setImportProgress(0);
      for (let i = 0; i < selecionados.length; i += 1) {
        await importEvolutionGroups([selecionados[i]]);
        setImportProgress(i + 1);
        setStatus(`Importando ${i + 1}/${selecionados.length}...`);
      }
      setStatus("Importação concluída! Atualizando lista...");
      router.refresh();
      setTimeout(onClose, 1200);
    } catch (error: any) {
      setStatus(error.message ?? "Erro ao importar grupos.");
    } finally {
      setImporting(false);
    }
  }

  const maxPage = Math.ceil(total / pageSize) || 1;

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-header">
          <h3>Sincronizar grupos da Evolution</h3>
          <button type="button" className="secondary" onClick={onClose}>
            Fechar
          </button>
        </div>

        <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem" }}>
          <div style={{ flex: 1, position: "relative" }}>
            <input
              placeholder="Buscar grupos por nome"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: "2.5rem" }}
            />
            <span
              style={{
                position: "absolute",
                left: "0.9rem",
                top: "50%",
                transform: "translateY(-50%)",
                color: "var(--text-muted)"
              }}
            >
              🔎
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <button type="button" className="secondary" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>
              ◀
            </button>
            <span>
              Página {page} / {maxPage}
            </span>
            <button
              type="button"
              className="secondary"
              disabled={page >= maxPage}
              onClick={() => setPage((p) => Math.min(maxPage, p + 1))}
            >
              ▶
            </button>
          </div>
        </div>

        <div style={{ maxHeight: "320px", overflowY: "auto", border: "1px solid var(--border)", borderRadius: "8px" }}>
          {loading ? (
            <div className="progress-wrapper" style={{ padding: "1rem" }}>
              <div className="progress-bar">
                <div className="progress-bar-fill" style={{ width: `${loadProgress}%` }} />
              </div>
              <span>{loadProgress}%</span>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th></th>
                  <th>Nome</th>
                  <th>Group ID</th>
                  <th>CR</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((grupo) => (
                  <tr key={grupo.group_id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={state[grupo.group_id]?.selected ?? false}
                        onChange={() => toggleSelect(grupo)}
                      />
                    </td>
                    <td>{grupo.nome}</td>
                    <td>{grupo.group_id}</td>
                    <td>
                      <input
                        placeholder="Informe o CR"
                        value={state[grupo.group_id]?.cr ?? ""}
                        onChange={(e) => updateCr(grupo.group_id, e.target.value)}
                      />
                    </td>
                  </tr>
                ))}
                {!filtered.length && (
                  <tr>
                    <td colSpan={4} style={{ textAlign: "center", padding: "1rem" }}>
                      Nenhum grupo encontrado.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>

        {status && <p style={{ marginTop: "0.75rem" }}>{status}</p>}
        {importTotal > 0 && (
          <div className="progress-wrapper">
            <div className="progress-bar">
              <div className="progress-bar-fill" style={{ width: `${Math.round((importProgress / importTotal) * 100)}%` }} />
            </div>
            <span>
              {importProgress}/{importTotal}
            </span>
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem", marginTop: "1rem" }}>
          <button type="button" className="secondary" onClick={onClose}>
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleImport}
            disabled={importing || loading || importTotal > 0 || !Object.values(state).some((item) => item.selected)}
          >
            {importing ? "Importando..." : "Importar selecionados"}
          </button>
        </div>
      </div>
    </div>
  );
}
