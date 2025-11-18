"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import type { Grupo } from "../lib/api";
import { deleteGroups } from "../lib/api";
import EvolutionModal from "./EvolutionModal";
import StructureSyncModal from "./StructureSyncModal";
import EditGroupModal from "./EditGroupModal";
import GroupTable from "./GroupTable";
import { FaCloudDownloadAlt, FaDatabase, FaTrash } from "react-icons/fa";

type Props = {
  grupos: Grupo[];
  filtros: Record<string, string[]>;
};

type FiltroState = {
  diretor_executivo?: string;
  diretor_regional?: string;
  gerente_regional?: string;
  gerente?: string;
  supervisor?: string;
  cliente?: string;
  pec_01?: string;
  pec_02?: string;
};

export default function GroupsPageClient({ grupos, filtros }: Props) {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [selectedFilters, setSelectedFilters] = useState<FiltroState>({});
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [evolutionOpen, setEvolutionOpen] = useState(false);
  const [structureOpen, setStructureOpen] = useState(false);
  const [editGroup, setEditGroup] = useState<Grupo | null>(null);
  const [actionStatus, setActionStatus] = useState<string | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const filteredGroups = useMemo(() => {
    const text = search.trim().toLowerCase();
    return grupos.filter((grupo) => {
      const matchesSearch =
        !text ||
        grupo.nome_grupo.toLowerCase().includes(text) ||
        grupo.group_id.toLowerCase().includes(text) ||
        (grupo.cr ?? "").toLowerCase().includes(text);

      if (!matchesSearch) return false;

      return Object.entries(selectedFilters).every(([key, value]) => {
        if (!value) return true;
        const campo = (grupo as any)[key] ?? "";
        return campo === value;
      });
    });
  }, [grupos, search, selectedFilters]);

  function handleFilterChange(key: keyof FiltroState, value: string) {
    setSelectedFilters((prev) => ({
      ...prev,
      [key]: value || undefined
    }));
  }

  function toggleSelection(id: number) {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  }

  function toggleSelectAll(ids: number[]) {
    if (!ids.length) return;
    const allSelected = ids.every((id) => selectedIds.includes(id));
    if (allSelected) {
      setSelectedIds((prev) => prev.filter((id) => !ids.includes(id)));
    } else {
      setSelectedIds((prev) => Array.from(new Set([...prev, ...ids])));
    }
  }

  async function handleDelete() {
    if (!selectedIds.length) return;
    if (!window.confirm(`Remover ${selectedIds.length} grupo(s)?`)) return;
    setDeleteLoading(true);
    setActionStatus("Removendo grupos selecionados...");
    try {
      await deleteGroups(selectedIds);
      setActionStatus("Grupos removidos.");
      setSelectedIds([]);
      router.refresh();
    } catch (error: any) {
      setActionStatus(error.message ?? "Erro ao remover grupos.");
    } finally {
      setDeleteLoading(false);
    }
  }

  return (
    <div className="grid" style={{ gap: "1.5rem" }}>
      <section className="panel" style={{ display: "grid", gap: "1rem" }}>
        <h2>Grupos WhatsApp</h2>
        <div style={{ position: "relative" }}>
          <input
            placeholder="Pesquisar por nome, group_id ou CR"
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
            🔍
          </span>
        </div>

        <div style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end", flexWrap: "wrap" }}>
          <button
            type="button"
            className="secondary"
            onClick={() => {
              setSearch("");
              setSelectedFilters({});
            }}
          >
            Limpar filtros
          </button>
          <button type="button" onClick={() => setStructureOpen(true)}>
            <FaDatabase style={{ marginRight: "0.35rem" }} />
            Sincronizar estrutura
          </button>
          <button type="button" onClick={() => setEvolutionOpen(true)}>
            <FaCloudDownloadAlt style={{ marginRight: "0.35rem" }} />
            Sincronizar Evolution
          </button>
          <button
            type="button"
            className="secondary"
            disabled={!selectedIds.length || deleteLoading}
            onClick={handleDelete}
          >
            <FaTrash style={{ marginRight: "0.35rem" }} />
            {deleteLoading ? "Excluindo..." : `Excluir (${selectedIds.length || 0})`}
          </button>
        </div>

        <div className="filters-grid">
          {(
            [
              ["diretor_executivo", "Diretor Executivo"],
              ["diretor_regional", "Diretor Regional"],
              ["gerente_regional", "Gerente Regional"],
              ["gerente", "Gerente"],
              ["supervisor", "Supervisor"],
              ["cliente", "Cliente"],
              ["pec_01", "PEC 01"],
              ["pec_02", "PEC 02"]
            ] as Array<[keyof FiltroState, string]>
          ).map(([key, label]) => (
            <label key={key}>
              {label}
              <select value={selectedFilters[key] ?? ""} onChange={(e) => handleFilterChange(key, e.target.value)}>
                <option value="">Todos</option>
                {(filtros[key === "cliente" ? "cliente" : key] ?? []).map((valor) => (
                  <option key={valor} value={valor}>
                    {valor}
                  </option>
                ))}
              </select>
            </label>
          ))}
        </div>
      </section>

      <section className="panel">
        <GroupTable
          grupos={filteredGroups}
          selectedIds={selectedIds}
          onToggle={toggleSelection}
          onToggleAll={toggleSelectAll}
          onEdit={(grupo) => setEditGroup(grupo)}
        />
      </section>

      {actionStatus && <p style={{ color: "var(--text-muted)" }}>{actionStatus}</p>}

      {evolutionOpen && <EvolutionModal onClose={() => setEvolutionOpen(false)} />}
      {structureOpen && <StructureSyncModal onClose={() => setStructureOpen(false)} />}
      {editGroup && <EditGroupModal grupo={editGroup} onClose={() => setEditGroup(null)} />}
    </div>
  );
}
