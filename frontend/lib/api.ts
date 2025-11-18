import { clientApi } from "./client";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.API_BASE_URL ?? "http://localhost:5000/api";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {})
      },
      cache: "no-store",
      next: { revalidate: 0 }
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Erro na API (${res.status}): ${text}`);
    }

    return res.json() as Promise<T>;
  } catch (error) {
    console.error("Falha ao buscar API", error);
    if (
      error instanceof TypeError ||
      (error instanceof Error && error.message.toLowerCase().includes("fetch failed"))
    ) {
      throw new Error(
        `Não foi possível conectar à API (${API_BASE}). Verifique se o backend FastAPI está rodando e se NEXT_PUBLIC_API_BASE_URL está configurado.`
      );
    }
    throw error;
  }
}

export type OverviewStats = {
  total_grupos: number;
  total_mensagens: number;
  total_envios: number;
  generated_at: string;
};

export async function getStats(): Promise<OverviewStats> {
  return apiFetch<OverviewStats>("/stats");
}

export async function getDashboardResumo(params?: URLSearchParams) {
  const query = params ? `?${params.toString()}` : "";
  return apiFetch<{ data: any; periodo: any }>("/dashboard/resumo" + query);
}

export async function getDashboardTarefas(params?: URLSearchParams) {
  const query = params ? `?${params.toString()}` : "";
  return apiFetch<{ data: any[] }>("/dashboard/tarefas-mes" + query);
}

export async function getDashboardPizza(params?: URLSearchParams) {
  const query = params ? `?${params.toString()}` : "";
  return apiFetch<{ data: Record<string, number> }>("/dashboard/pizza" + query);
}

export type Grupo = {
  id: number;
  group_id: string;
  nome_grupo: string;
  envio: boolean;
  cr?: string | null;
  cliente?: string | null;
  pec_01?: string | null;
  pec_02?: string | null;
  diretor_executivo?: string | null;
  diretor_regional?: string | null;
  gerente_regional?: string | null;
  gerente?: string | null;
  supervisor?: string | null;
};

export async function getGrupos(): Promise<Grupo[]> {
  return apiFetch<Grupo[]>("/grupos");
}

export async function getGrupoFiltros() {
  return apiFetch("/grupos/filtros/meta");
}

export type Agendamento = {
  id: number;
  grupo_id: number;
  nome_grupo: string;
  cr: string | null;
  tipo_envio: string;
  dias_semana: string | null;
  data_envio: string;
  hora_inicio: string;
  hora_fim: string;
  ativo: boolean;
};

export async function getAgendamentos(): Promise<Agendamento[]> {
  return apiFetch<Agendamento[]>("/agendamentos");
}

export type Mensagem = {
  id: number;
  mensagem: string;
  grupos_ids: string[];
  tipo_recorrencia: string;
  dias_semana: number[] | null;
  horario: string;
  data_inicio: string;
  data_fim: string | null;
  ativo: boolean;
};

export async function getMensagens(params?: string): Promise<Mensagem[]> {
  const suffix = params ? `?${params}` : "";
  return apiFetch<Mensagem[]>(`/mensagens${suffix}`);
}

export async function getSlaPreview(grupoId: number, payload: any) {
  return apiFetch(`/sla/preview/${grupoId}`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export type EnvioGrupo = {
  id: number;
  group_id: string;
  nome_grupo: string;
  envio: boolean;
  cr?: string | null;
};

export async function getEnvioGrupos(): Promise<EnvioGrupo[]> {
  return apiFetch<EnvioGrupo[]>("/envio/grupos");
}

export type EvolutionGroup = {
  group_id: string;
  nome: string;
  cr?: string | null;
};

export type EvolutionGroupsResponse = {
  total: number;
  page: number;
  page_size: number;
  grupos: EvolutionGroup[];
};

export async function getEvolutionGroups(page = 1, pageSize = 25): Promise<EvolutionGroupsResponse> {
  return apiFetch(`/evolution/groups?page=${page}&page_size=${pageSize}`);
}

export async function importEvolutionGroups(grupos: EvolutionGroup[]) {
  return clientApi.post("/evolution/import", { grupos });
}

export type GrupoCrItem = {
  id: number;
  nome_grupo: string;
  cr: string;
};

export async function getGroupsWithCR(): Promise<GrupoCrItem[]> {
  return apiFetch<GrupoCrItem[]>("/grupos/com-cr");
}

export async function syncGroupStructure(grupoId: number) {
  return clientApi.post(`/grupos/${grupoId}/sync-estrutura`);
}

export async function deleteGroups(ids: number[]) {
  return clientApi.delete<{ removidos: number }>("/grupos", { ids });
}
