"use client";

import { useEffect, useState } from "react";
import { getGroupsWithCR, syncGroupStructure, type GrupoCrItem } from "../lib/api";
import { useRouter } from "next/navigation";

type Props = {
  onClose: () => void;
};

export default function StructureSyncModal({ onClose }: Props) {
  const router = useRouter();
  const [groups, setGroups] = useState<GrupoCrItem[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<string | null>("Carregando grupos com CR...");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await getGroupsWithCR();
        if (!cancelled) {
          setGroups(data);
          setStatus(`Encontrados ${data.length} grupo(s) com CR. Iniciando sincronização...`);
          setLoaded(true);
        }
      } catch (err: any) {
        if (!cancelled) setError(err?.message ?? "Erro ao buscar grupos.");
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function sync() {
      if (!loaded || !groups.length) {
        if (loaded) {
          setStatus("Nenhum grupo com CR encontrado.");
        }
        return;
      }
      for (let i = 0; i < groups.length; i += 1) {
        if (cancelled) break;
        const grupo = groups[i];
        try {
          await syncGroupStructure(grupo.id);
          setProgress(i + 1);
          setStatus(`Sincronizando ${grupo.nome_grupo} (${i + 1}/${groups.length})`);
        } catch (err: any) {
          setError(err?.message ?? `Falha ao sincronizar ${grupo.nome_grupo}`);
          break;
        }
      }
      if (!cancelled) {
        setStatus("Sincronização concluída!");
        router.refresh();
        setTimeout(onClose, 1200);
      }
    }
    if (loaded) {
      sync();
    }
    return () => {
      cancelled = true;
    };
  }, [loaded, groups, router]);

  const total = groups.length || 1;
  const percent = Math.min(100, Math.round((progress / total) * 100));

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-header">
          <h3>Sincronizar estrutura (Vista)</h3>
          <button type="button" className="secondary" onClick={onClose}>
            Fechar
          </button>
        </div>
        <p>{status}</p>
        <div className="progress-wrapper">
          <div className="progress-bar">
            <div className="progress-bar-fill" style={{ width: `${percent}%` }} />
          </div>
          <span>{percent}%</span>
        </div>
        {error && <p style={{ color: "#f87171" }}>{error}</p>}
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
          Este processo atualiza Diretor Executivo, Diretor Regional, Cliente etc. com base no CR de cada grupo.
        </p>
      </div>
    </div>
  );
}
