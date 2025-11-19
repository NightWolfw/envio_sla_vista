import { clientApi } from "./client";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://soloalive.uk/api";

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
  envio_pdf: boolean;
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

export type GrupoFiltros = Record<string, string[]>;

export async function getGrupoFiltros(): Promise<GrupoFiltros> {
  return apiFetch<GrupoFiltros>("/grupos/filtros/meta");
}

export type Agendamento = {
  id: number;
  grupo_id: number;
  nome_grupo: string;
  cr: string | null;
  tipo_envio: string;
  dias_semana: string | null;
  data_envio: string;
  proximo_envio?: string | null;
  hora_inicio: string;
  dia_offset_inicio: number;
  hora_fim: string;
  dia_offset_fim: number;
  ativo: boolean;
  criado_em?: string;
  atualizado_em?: string | null;
  ultimo_status?: string | null;
  ultimo_envio?: string | null;
  ultimo_erro?: string | null;
};

export type AgendamentoListResponse = {
  items: Agendamento[];
  total: number;
  page: number;
  page_size: number;
};

export type AgendamentoFilters = {
  page?: number;
  page_size?: number;
  tipo_envio?: string;
  ativo?: boolean | string;
  grupo?: string;
  cr?: string;
  dia?: string;
  data_inicio?: string;
  data_fim?: string;
};

export type EnviarAgoraResponse = {
  id: number;
  status: string;
  message: string;
};

export type PdfLinkResponse = {
  id: number;
  url: string;
};

export type PdfBulkResponse = {
  successes: PdfLinkResponse[];
  failures: number[];
};

export type BulkDeleteResponse = {
  removed: number;
  failures: number[];
};

function buildQuery(params: Record<string, any>): string {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return;
    query.set(key, String(value));
  });
  const text = query.toString();
  return text ? `?${text}` : "";
}

export async function getAgendamentos(filters?: AgendamentoFilters): Promise<Agendamento[]> {
  const response = await getAgendamentosPaged(filters);
  return response.items;
}

export async function getAgendamentosPaged(filters?: AgendamentoFilters): Promise<AgendamentoListResponse> {
  const query = buildQuery(filters ?? {});
  return apiFetch<AgendamentoListResponse>(`/agendamentos${query}`);
}

export type AgendamentoPayload = {
  grupo_id: number;
  tipo_envio: "resultados" | "programadas";
  dias_semana: string[];
  data_envio: string;
  hora_inicio: string;
  dia_offset_inicio: number;
  hora_fim: string;
  dia_offset_fim: number;
};

export async function createAgendamento(payload: AgendamentoPayload) {
  return clientApi.post("/agendamentos", payload);
}

export async function updateAgendamento(id: number, payload: AgendamentoPayload & { ativo?: boolean }) {
  return clientApi.put(`/agendamentos/${id}`, payload);
}

export async function deleteAgendamento(id: number) {
  return clientApi.delete(`/agendamentos/${id}`);
}

export async function cloneAgendamento(id: number) {
  return clientApi.post<{ id: number }>(`/agendamentos/${id}/clone`);
}

export async function pauseAgendamento(id: number) {
  return clientApi.post<{ id: number; ativo: boolean }>(`/agendamentos/${id}/pause`);
}

export async function resumeAgendamento(id: number) {
  return clientApi.post<{ id: number; ativo: boolean }>(`/agendamentos/${id}/resume`);
}

export async function sendAgendamentoNow(id: number) {
  return clientApi.post<EnviarAgoraResponse>(`/agendamentos/${id}/send-now`);
}

export async function generatePdfAgendamento(id: number) {
  return clientApi.post<PdfLinkResponse>(`/agendamentos/${id}/pdf`);
}

export async function generatePdfBulk(ids: number[]) {
  return clientApi.post<PdfBulkResponse>("/agendamentos/bulk/pdf", { ids });
}

export async function deleteAgendamentosBulk(ids: number[]) {
  return clientApi.delete<BulkDeleteResponse>("/agendamentos/bulk", { ids });
}

export type AgendamentoLog = {
  id: number;
  data_envio: string;
  status: string;
  mensagem_enviada: string | null;
  resposta_api: string | null;
  erro: string | null;
  criado_em: string;
  nome_grupo?: string | null;
};

export type AgendamentoLogResponse = {
  items: AgendamentoLog[];
  total: number;
  page: number;
  page_size: number;
};

export async function getAgendamentoLogs(agendamentoId: number, page = 1, pageSize = 10) {
  const query = buildQuery({ page, page_size: pageSize });
  return apiFetch<AgendamentoLogResponse>(`/agendamentos/${agendamentoId}/logs${query}`);
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

export type SlaTemplate = {
  resultados: string;
  programadas: string;
};

export async function fetchSlaTemplate(): Promise<SlaTemplate> {
  return apiFetch<SlaTemplate>("/sla/template");
}

export async function updateSlaTemplate(payload: SlaTemplate): Promise<SlaTemplate> {
  return clientApi.put<SlaTemplate>("/sla/template", payload);
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

export async function getAllEvolutionGroups(): Promise<EvolutionGroupsResponse> {
  return apiFetch("/evolution/groups/all");
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
