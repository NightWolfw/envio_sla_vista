module.exports = [
"[project]/frontend/lib/client.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "clientApi",
    ()=>clientApi
]);
"use client";
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:5000/api";
async function request(path, method, body) {
    const res = await fetch(`${API_BASE}${path}`, {
        method,
        headers: {
            "Content-Type": "application/json"
        },
        body: body ? JSON.stringify(body) : undefined
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Erro ${res.status}`);
    }
    if (res.status === 204) {
        return {};
    }
    return res.json();
}
const clientApi = {
    put: (path, body)=>request(path, "PUT", body),
    post: (path, body)=>request(path, "POST", body),
    delete: (path, body)=>request(path, "DELETE", body)
};
}),
"[project]/frontend/lib/api.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "cloneAgendamento",
    ()=>cloneAgendamento,
    "createAgendamento",
    ()=>createAgendamento,
    "deleteAgendamento",
    ()=>deleteAgendamento,
    "deleteGroups",
    ()=>deleteGroups,
    "fetchSlaTemplate",
    ()=>fetchSlaTemplate,
    "getAgendamentoLogs",
    ()=>getAgendamentoLogs,
    "getAgendamentos",
    ()=>getAgendamentos,
    "getAgendamentosPaged",
    ()=>getAgendamentosPaged,
    "getAllEvolutionGroups",
    ()=>getAllEvolutionGroups,
    "getDashboardPizza",
    ()=>getDashboardPizza,
    "getDashboardResumo",
    ()=>getDashboardResumo,
    "getDashboardTarefas",
    ()=>getDashboardTarefas,
    "getEnvioGrupos",
    ()=>getEnvioGrupos,
    "getEvolutionGroups",
    ()=>getEvolutionGroups,
    "getGroupsWithCR",
    ()=>getGroupsWithCR,
    "getGrupoFiltros",
    ()=>getGrupoFiltros,
    "getGrupos",
    ()=>getGrupos,
    "getMensagens",
    ()=>getMensagens,
    "getSlaPreview",
    ()=>getSlaPreview,
    "getStats",
    ()=>getStats,
    "importEvolutionGroups",
    ()=>importEvolutionGroups,
    "pauseAgendamento",
    ()=>pauseAgendamento,
    "resumeAgendamento",
    ()=>resumeAgendamento,
    "syncGroupStructure",
    ()=>syncGroupStructure,
    "updateAgendamento",
    ()=>updateAgendamento,
    "updateSlaTemplate",
    ()=>updateSlaTemplate
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/lib/client.ts [app-ssr] (ecmascript)");
;
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.API_BASE_URL ?? "http://localhost:5000/api";
async function apiFetch(path, init) {
    try {
        const res = await fetch(`${API_BASE}${path}`, {
            ...init,
            headers: {
                "Content-Type": "application/json",
                ...init?.headers ?? {}
            },
            cache: "no-store",
            next: {
                revalidate: 0
            }
        });
        if (!res.ok) {
            const text = await res.text();
            throw new Error(`Erro na API (${res.status}): ${text}`);
        }
        return res.json();
    } catch (error) {
        console.error("Falha ao buscar API", error);
        if (error instanceof TypeError || error instanceof Error && error.message.toLowerCase().includes("fetch failed")) {
            throw new Error(`Não foi possível conectar à API (${API_BASE}). Verifique se o backend FastAPI está rodando e se NEXT_PUBLIC_API_BASE_URL está configurado.`);
        }
        throw error;
    }
}
async function getStats() {
    return apiFetch("/stats");
}
async function getDashboardResumo(params) {
    const query = params ? `?${params.toString()}` : "";
    return apiFetch("/dashboard/resumo" + query);
}
async function getDashboardTarefas(params) {
    const query = params ? `?${params.toString()}` : "";
    return apiFetch("/dashboard/tarefas-mes" + query);
}
async function getDashboardPizza(params) {
    const query = params ? `?${params.toString()}` : "";
    return apiFetch("/dashboard/pizza" + query);
}
async function getGrupos() {
    return apiFetch("/grupos");
}
async function getGrupoFiltros() {
    return apiFetch("/grupos/filtros/meta");
}
function buildQuery(params) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value])=>{
        if (value === undefined || value === null || value === "") return;
        query.set(key, String(value));
    });
    const text = query.toString();
    return text ? `?${text}` : "";
}
async function getAgendamentos(filters) {
    const response = await getAgendamentosPaged(filters);
    return response.items;
}
async function getAgendamentosPaged(filters) {
    const query = buildQuery(filters ?? {});
    return apiFetch(`/agendamentos${query}`);
}
async function createAgendamento(payload) {
    return __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clientApi"].post("/agendamentos", payload);
}
async function updateAgendamento(id, payload) {
    return __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clientApi"].put(`/agendamentos/${id}`, payload);
}
async function deleteAgendamento(id) {
    return __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clientApi"].delete(`/agendamentos/${id}`);
}
async function cloneAgendamento(id) {
    return __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clientApi"].post(`/agendamentos/${id}/clone`);
}
async function pauseAgendamento(id) {
    return __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clientApi"].post(`/agendamentos/${id}/pause`);
}
async function resumeAgendamento(id) {
    return __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clientApi"].post(`/agendamentos/${id}/resume`);
}
async function getAgendamentoLogs(agendamentoId, page = 1, pageSize = 10) {
    const query = buildQuery({
        page,
        page_size: pageSize
    });
    return apiFetch(`/agendamentos/${agendamentoId}/logs${query}`);
}
async function getMensagens(params) {
    const suffix = params ? `?${params}` : "";
    return apiFetch(`/mensagens${suffix}`);
}
async function getSlaPreview(grupoId, payload) {
    return apiFetch(`/sla/preview/${grupoId}`, {
        method: "POST",
        body: JSON.stringify(payload)
    });
}
async function fetchSlaTemplate() {
    return apiFetch("/sla/template");
}
async function updateSlaTemplate(payload) {
    return __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clientApi"].put("/sla/template", payload);
}
async function getEnvioGrupos() {
    return apiFetch("/envio/grupos");
}
async function getEvolutionGroups(page = 1, pageSize = 25) {
    return apiFetch(`/evolution/groups?page=${page}&page_size=${pageSize}`);
}
async function getAllEvolutionGroups() {
    return apiFetch("/evolution/groups/all");
}
async function importEvolutionGroups(grupos) {
    return __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clientApi"].post("/evolution/import", {
        grupos
    });
}
async function getGroupsWithCR() {
    return apiFetch("/grupos/com-cr");
}
async function syncGroupStructure(grupoId) {
    return __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clientApi"].post(`/grupos/${grupoId}/sync-estrutura`);
}
async function deleteGroups(ids) {
    return __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clientApi"].delete("/grupos", {
        ids
    });
}
}),
"[project]/frontend/components/envio-sla/constants.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "templateVariables",
    ()=>templateVariables,
    "tipoEnvioOptions",
    ()=>tipoEnvioOptions,
    "weekdayOptions",
    ()=>weekdayOptions
]);
const weekdayOptions = [
    {
        label: "Seg",
        value: "seg"
    },
    {
        label: "Ter",
        value: "ter"
    },
    {
        label: "Qua",
        value: "qua"
    },
    {
        label: "Qui",
        value: "qui"
    },
    {
        label: "Sex",
        value: "sex"
    },
    {
        label: "Sáb",
        value: "sab"
    },
    {
        label: "Dom",
        value: "dom"
    }
];
const tipoEnvioOptions = [
    {
        label: "Resultados",
        value: "resultados"
    },
    {
        label: "Programadas",
        value: "programadas"
    }
];
const templateVariables = [
    "{{saudacao}}",
    "{{periodo_inicio}}",
    "{{periodo_fim}}",
    "{{periodo_completo}}",
    "{{finalizadas}}",
    "{{nao_realizadas}}",
    "{{em_aberto}}",
    "{{iniciadas}}",
    "{{total}}",
    "{{total_programadas}}",
    "{{porcentagem}}",
    "{{emoji}}",
    "{{feedback}}",
    "{{data_envio}}"
];
}),
"[project]/frontend/components/envio-sla/AgendamentoModal.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>AgendamentoModal
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/lib/api.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$components$2f$envio$2d$sla$2f$constants$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/components/envio-sla/constants.ts [app-ssr] (ecmascript)");
"use client";
;
;
;
;
function AgendamentoModal({ mode, agendamento, onClose, onSaved }) {
    const [grupos, setGrupos] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(true);
    const [saving, setSaving] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [form, setForm] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(()=>{
        if (!agendamento) {
            return {
                grupo_id: 0,
                tipo_envio: "resultados",
                dias_semana: [],
                data_envio: "",
                hora_inicio: "08:00",
                dia_offset_inicio: 0,
                hora_fim: "18:00",
                dia_offset_fim: 0
            };
        }
        return {
            grupo_id: agendamento.grupo_id,
            tipo_envio: agendamento.tipo_envio,
            dias_semana: agendamento.dias_semana ? agendamento.dias_semana.split(",").map((d)=>d.trim()).filter(Boolean) : [],
            data_envio: toDateInput(agendamento.data_envio),
            hora_inicio: agendamento.hora_inicio?.slice(0, 5) ?? "08:00",
            dia_offset_inicio: agendamento.dia_offset_inicio ?? 0,
            hora_fim: agendamento.hora_fim?.slice(0, 5) ?? "18:00",
            dia_offset_fim: agendamento.dia_offset_fim ?? 0
        };
    });
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        async function load() {
            try {
                const data = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getGrupos"])();
                setGrupos(data);
            } catch (err) {
                setError(err.message ?? "Erro ao carregar grupos disponíveis.");
            } finally{
                setLoading(false);
            }
        }
        load();
    }, []);
    const handleSubmit = async (event)=>{
        event.preventDefault();
        if (!form.grupo_id) {
            setError("Selecione um grupo.");
            return;
        }
        if (!form.data_envio) {
            setError("Informe a primeira data de envio.");
            return;
        }
        setSaving(true);
        setError(null);
        const payload = {
            ...form,
            data_envio: new Date(form.data_envio).toISOString(),
            hora_inicio: normalizeTime(form.hora_inicio),
            hora_fim: normalizeTime(form.hora_fim)
        };
        try {
            if (mode === "edit" && agendamento) {
                await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["updateAgendamento"])(agendamento.id, payload);
                onSaved("Agendamento atualizado.");
            } else {
                await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createAgendamento"])(payload);
                onSaved("Agendamento criado.");
            }
        } catch (err) {
            setError(err.message ?? "Erro ao salvar agendamento.");
        } finally{
            setSaving(false);
        }
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "modal-backdrop",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "modal max-h-[90vh] w-full max-w-3xl overflow-y-auto",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "modal-header",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                            children: mode === "create" ? "Novo agendamento SLA" : `Editar ${agendamento?.nome_grupo}`
                        }, void 0, false, {
                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                            lineNumber: 104,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            className: "secondary",
                            onClick: onClose,
                            children: "Fechar"
                        }, void 0, false, {
                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                            lineNumber: 105,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                    lineNumber: 103,
                    columnNumber: 9
                }, this),
                loading ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: "text-sm text-textMuted",
                    children: "Carregando grupos..."
                }, void 0, false, {
                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                    lineNumber: 110,
                    columnNumber: 11
                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                    className: "grid gap-4",
                    onSubmit: handleSubmit,
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                            className: "text-sm font-semibold",
                            children: [
                                "Grupo",
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                    className: "mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text",
                                    value: form.grupo_id || "",
                                    onChange: (e)=>setForm((prev)=>({
                                                ...prev,
                                                grupo_id: Number(e.target.value)
                                            })),
                                    required: true,
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                            value: "",
                                            children: "Selecione o grupo"
                                        }, void 0, false, {
                                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                            lineNumber: 121,
                                            columnNumber: 17
                                        }, this),
                                        grupos.map((grupo)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: grupo.id,
                                                children: grupo.nome_grupo
                                            }, grupo.id, false, {
                                                fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                                lineNumber: 123,
                                                columnNumber: 19
                                            }, this))
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                    lineNumber: 115,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                            lineNumber: 113,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "grid gap-4 md:grid-cols-2",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                    className: "text-sm font-semibold",
                                    children: [
                                        "Tipo de envio",
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                            className: "mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text",
                                            value: form.tipo_envio,
                                            onChange: (e)=>setForm((prev)=>({
                                                        ...prev,
                                                        tipo_envio: e.target.value
                                                    })),
                                            children: __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$components$2f$envio$2d$sla$2f$constants$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["tipoEnvioOptions"].map((opt)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                    value: opt.value,
                                                    children: opt.label
                                                }, opt.value, false, {
                                                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                                    lineNumber: 138,
                                                    columnNumber: 21
                                                }, this))
                                        }, void 0, false, {
                                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                            lineNumber: 132,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                    lineNumber: 130,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                    className: "text-sm font-semibold",
                                    children: [
                                        "Primeira execução",
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "datetime-local",
                                            className: "mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text",
                                            value: form.data_envio,
                                            onChange: (e)=>setForm((prev)=>({
                                                        ...prev,
                                                        data_envio: e.target.value
                                                    })),
                                            required: true
                                        }, void 0, false, {
                                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                            lineNumber: 146,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                    lineNumber: 144,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                            lineNumber: 129,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("fieldset", {
                            className: "rounded-xl border border-border/60 p-3",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("legend", {
                                    className: "px-2 text-sm font-semibold text-text",
                                    children: "Dias da semana"
                                }, void 0, false, {
                                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                    lineNumber: 156,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: "flex flex-wrap gap-3 text-sm",
                                    children: __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$components$2f$envio$2d$sla$2f$constants$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["weekdayOptions"].map((opt)=>{
                                        const checked = form.dias_semana.includes(opt.value);
                                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                            className: "flex items-center gap-2",
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    type: "checkbox",
                                                    checked: checked,
                                                    onChange: (e)=>{
                                                        setForm((prev)=>{
                                                            const dias = new Set(prev.dias_semana);
                                                            if (e.target.checked) dias.add(opt.value);
                                                            else dias.delete(opt.value);
                                                            return {
                                                                ...prev,
                                                                dias_semana: Array.from(dias)
                                                            };
                                                        });
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                                    lineNumber: 162,
                                                    columnNumber: 23
                                                }, this),
                                                opt.label
                                            ]
                                        }, opt.value, true, {
                                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                            lineNumber: 161,
                                            columnNumber: 21
                                        }, this);
                                    })
                                }, void 0, false, {
                                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                    lineNumber: 157,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                            lineNumber: 155,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "grid gap-4 md:grid-cols-2",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                    className: "text-sm font-semibold",
                                    children: [
                                        "Hora inicial",
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "time",
                                            className: "mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text",
                                            value: form.hora_inicio,
                                            onChange: (e)=>setForm((prev)=>({
                                                        ...prev,
                                                        hora_inicio: e.target.value
                                                    }))
                                        }, void 0, false, {
                                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                            lineNumber: 183,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                    lineNumber: 181,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                    className: "text-sm font-semibold",
                                    children: [
                                        "Offset início (dias)",
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "number",
                                            className: "mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text",
                                            value: form.dia_offset_inicio,
                                            onChange: (e)=>setForm((prev)=>({
                                                        ...prev,
                                                        dia_offset_inicio: Number(e.target.value)
                                                    }))
                                        }, void 0, false, {
                                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                            lineNumber: 192,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                    lineNumber: 190,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                    className: "text-sm font-semibold",
                                    children: [
                                        "Hora final",
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "time",
                                            className: "mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text",
                                            value: form.hora_fim,
                                            onChange: (e)=>setForm((prev)=>({
                                                        ...prev,
                                                        hora_fim: e.target.value
                                                    }))
                                        }, void 0, false, {
                                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                            lineNumber: 201,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                    lineNumber: 199,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                    className: "text-sm font-semibold",
                                    children: [
                                        "Offset fim (dias)",
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "number",
                                            className: "mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text",
                                            value: form.dia_offset_fim,
                                            onChange: (e)=>setForm((prev)=>({
                                                        ...prev,
                                                        dia_offset_fim: Number(e.target.value)
                                                    }))
                                        }, void 0, false, {
                                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                            lineNumber: 210,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                    lineNumber: 208,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                            lineNumber: 180,
                            columnNumber: 13
                        }, this),
                        error && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "text-sm text-rose-300",
                            children: error
                        }, void 0, false, {
                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                            lineNumber: 218,
                            columnNumber: 23
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex justify-end gap-3",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "button",
                                    className: "secondary",
                                    onClick: onClose,
                                    children: "Cancelar"
                                }, void 0, false, {
                                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                    lineNumber: 220,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "submit",
                                    disabled: saving,
                                    className: "rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-slate-900",
                                    children: saving ? "Salvando..." : "Salvar"
                                }, void 0, false, {
                                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                                    lineNumber: 223,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                            lineNumber: 219,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
                    lineNumber: 112,
                    columnNumber: 11
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
            lineNumber: 102,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/frontend/components/envio-sla/AgendamentoModal.tsx",
        lineNumber: 101,
        columnNumber: 5
    }, this);
}
function toDateInput(value) {
    if (!value) return "";
    const date = new Date(value);
    return date.toISOString().slice(0, 16);
}
function normalizeTime(value) {
    if (!value) return "00:00";
    return value.length === 5 ? `${value}:00` : value;
}
}),
"[project]/frontend/components/envio-sla/EnvioSlaView.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>EnvioSlaView
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/lib/api.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$components$2f$envio$2d$sla$2f$constants$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/components/envio-sla/constants.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$components$2f$envio$2d$sla$2f$AgendamentoModal$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/components/envio-sla/AgendamentoModal.tsx [app-ssr] (ecmascript)");
(()=>{
    const e = new Error("Cannot find module './LogsModal'");
    e.code = 'MODULE_NOT_FOUND';
    throw e;
})();
(()=>{
    const e = new Error("Cannot find module './TemplateModal'");
    e.code = 'MODULE_NOT_FOUND';
    throw e;
})();
(()=>{
    const e = new Error("Cannot find module './ConfirmModal'");
    e.code = 'MODULE_NOT_FOUND';
    throw e;
})();
"use client";
;
;
;
;
;
;
;
;
function EnvioSlaView() {
    const [page, setPage] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(1);
    const [pageSize, setPageSize] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(10);
    const [filters, setFilters] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])({
        grupo: "",
        cr: "",
        tipo_envio: "",
        status: "todos",
        dia: ""
    });
    const [pendingFilters, setPendingFilters] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(filters);
    const [agendamentos, setAgendamentos] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [total, setTotal] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(0);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(true);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [statusMessage, setStatusMessage] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [showFilters, setShowFilters] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [modal, setModal] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])({
        open: false,
        mode: "create"
    });
    const [logsState, setLogsState] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])({
        open: false
    });
    const [templateState, setTemplateState] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])({
        open: false,
        confirm: false,
        data: null,
        loading: false,
        saving: false,
        error: null
    });
    const totalPages = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useMemo"])(()=>Math.max(1, Math.ceil(total / pageSize)), [
        total,
        pageSize
    ]);
    const fetchAgendamentos = async ()=>{
        setLoading(true);
        setError(null);
        try {
            const payload = {
                page,
                page_size: pageSize,
                grupo: filters.grupo || undefined,
                cr: filters.cr || undefined,
                tipo_envio: filters.tipo_envio || undefined,
                dia: filters.dia || undefined
            };
            if (filters.status === "ativos") payload.ativo = true;
            if (filters.status === "pausados") payload.ativo = false;
            const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getAgendamentosPaged"])(payload);
            setAgendamentos(response.items);
            setTotal(response.total);
        } catch (err) {
            setError(err.message ?? "Erro ao carregar agendamentos.");
        } finally{
            setLoading(false);
        }
    };
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        fetchAgendamentos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [
        page,
        pageSize,
        filters
    ]);
    const refresh = async (message)=>{
        await fetchAgendamentos();
        if (message) {
            setStatusMessage(message);
            setTimeout(()=>setStatusMessage(null), 3000);
        }
    };
    const handleApplyFilters = (event)=>{
        event.preventDefault();
        setFilters(pendingFilters);
        setPage(1);
    };
    const handleResetFilters = ()=>{
        const clean = {
            grupo: "",
            cr: "",
            tipo_envio: "",
            status: "todos",
            dia: ""
        };
        setPendingFilters(clean);
        setFilters(clean);
        setPage(1);
    };
    const openCreateModal = ()=>setModal({
            open: true,
            mode: "create"
        });
    const openEditModal = (agendamento)=>setModal({
            open: true,
            mode: "edit",
            agendamento
        });
    const closeModal = ()=>setModal({
            open: false,
            mode: "create",
            agendamento: undefined
        });
    const handleDelete = async (agendamento)=>{
        if (!confirm(`Remover o agendamento do grupo ${agendamento.nome_grupo}?`)) return;
        try {
            await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["deleteAgendamento"])(agendamento.id);
            refresh("Agendamento removido.");
        } catch (err) {
            setStatusMessage(err.message ?? "Erro ao remover agendamento.");
        }
    };
    const handleClone = async (agendamento)=>{
        try {
            await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cloneAgendamento"])(agendamento.id);
            refresh("Agendamento clonado.");
        } catch (err) {
            setStatusMessage(err.message ?? "Erro ao clonar agendamento.");
        }
    };
    const handleToggleStatus = async (agendamento)=>{
        try {
            if (agendamento.ativo) {
                await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["pauseAgendamento"])(agendamento.id);
                refresh("Agendamento pausado.");
            } else {
                await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["resumeAgendamento"])(agendamento.id);
                refresh("Agendamento retomado.");
            }
        } catch (err) {
            setStatusMessage(err.message ?? "Erro ao alterar status.");
        }
    };
    const openLogs = (agendamento)=>setLogsState({
            open: true,
            agendamento
        });
    const closeLogs = ()=>setLogsState({
            open: false
        });
    const openTemplateConfirm = ()=>setTemplateState((prev)=>({
                ...prev,
                confirm: true
            }));
    const closeTemplateConfirm = ()=>setTemplateState((prev)=>({
                ...prev,
                confirm: false
            }));
    const ensureTemplateLoaded = async ()=>{
        setTemplateState((prev)=>({
                ...prev,
                loading: true,
                error: null
            }));
        try {
            const template = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["fetchSlaTemplate"])();
            setTemplateState((prev)=>({
                    ...prev,
                    data: template
                }));
        } catch (err) {
            setTemplateState((prev)=>({
                    ...prev,
                    error: err.message ?? "Erro ao carregar template."
                }));
        } finally{
            setTemplateState((prev)=>({
                    ...prev,
                    loading: false
                }));
        }
    };
    const openTemplateModal = async ()=>{
        closeTemplateConfirm();
        setTemplateState((prev)=>({
                ...prev,
                open: true
            }));
        if (!templateState.data) {
            await ensureTemplateLoaded();
        }
    };
    const closeTemplateModal = ()=>setTemplateState((prev)=>({
                ...prev,
                open: false
            }));
    const handleTemplateSave = async (template)=>{
        setTemplateState((prev)=>({
                ...prev,
                saving: true,
                error: null
            }));
        try {
            const updated = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["updateSlaTemplate"])(template);
            setTemplateState((prev)=>({
                    ...prev,
                    data: updated
                }));
            setStatusMessage("Template atualizado com sucesso.");
            closeTemplateModal();
        } catch (err) {
            setTemplateState((prev)=>({
                    ...prev,
                    error: err.message ?? "Erro ao salvar template."
                }));
        } finally{
            setTemplateState((prev)=>({
                    ...prev,
                    saving: false
                }));
        }
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "space-y-5",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("header", {
                className: "flex flex-wrap items-center justify-between gap-4",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                className: "text-sm uppercase tracking-wide text-textMuted/70",
                                children: "Operações"
                            }, void 0, false, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 205,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                                className: "text-3xl font-semibold text-white",
                                children: "Envio SLA"
                            }, void 0, false, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 206,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                className: "text-sm text-textMuted",
                                children: "Gerencie agendamentos, templates e logs de envio."
                            }, void 0, false, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 207,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                        lineNumber: 204,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex items-center gap-3",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: openTemplateConfirm,
                                className: "rounded-xl border border-border px-4 py-2 text-sm font-medium text-text transition hover:border-accent hover:text-accent",
                                children: "Configurações"
                            }, void 0, false, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 210,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: openCreateModal,
                                className: "rounded-xl bg-accent px-5 py-2 text-sm font-semibold text-slate-900 shadow-panel transition hover:bg-cyan-300",
                                children: "Novo Agendamento SLA"
                            }, void 0, false, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 217,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                        lineNumber: 209,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                lineNumber: 203,
                columnNumber: 7
            }, this),
            statusMessage && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-200",
                children: statusMessage
            }, void 0, false, {
                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                lineNumber: 228,
                columnNumber: 9
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("section", {
                className: "rounded-2xl border border-border/80 bg-surface/70 p-4 shadow-panel",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        onClick: ()=>setShowFilters((prev)=>!prev),
                        className: "flex w-full items-center justify-between rounded-xl border border-border px-4 py-2 text-left text-sm text-text transition hover:border-accent",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                children: "Filtro avançado"
                            }, void 0, false, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 239,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                children: showFilters ? "−" : "+"
                            }, void 0, false, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 240,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                        lineNumber: 234,
                        columnNumber: 9
                    }, this),
                    showFilters && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                        className: "mt-4 grid gap-3 md:grid-cols-2",
                        onSubmit: handleApplyFilters,
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                className: "flex flex-col text-sm",
                                children: [
                                    "Grupo",
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                        className: "mt-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text",
                                        value: pendingFilters.grupo,
                                        onChange: (e)=>setPendingFilters((prev)=>({
                                                    ...prev,
                                                    grupo: e.target.value
                                                }))
                                    }, void 0, false, {
                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                        lineNumber: 246,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 244,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                className: "flex flex-col text-sm",
                                children: [
                                    "CR",
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                        className: "mt-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text",
                                        value: pendingFilters.cr,
                                        onChange: (e)=>setPendingFilters((prev)=>({
                                                    ...prev,
                                                    cr: e.target.value
                                                }))
                                    }, void 0, false, {
                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                        lineNumber: 254,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 252,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                className: "flex flex-col text-sm",
                                children: [
                                    "Tipo de envio",
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                        className: "mt-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text",
                                        value: pendingFilters.tipo_envio,
                                        onChange: (e)=>setPendingFilters((prev)=>({
                                                    ...prev,
                                                    tipo_envio: e.target.value
                                                })),
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "",
                                                children: "Todos"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 267,
                                                columnNumber: 17
                                            }, this),
                                            __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$components$2f$envio$2d$sla$2f$constants$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["tipoEnvioOptions"].map((opt)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                    value: opt.value,
                                                    children: opt.label
                                                }, opt.value, false, {
                                                    fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                    lineNumber: 269,
                                                    columnNumber: 19
                                                }, this))
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                        lineNumber: 262,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 260,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                className: "flex flex-col text-sm",
                                children: [
                                    "Status",
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                        className: "mt-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text",
                                        value: pendingFilters.status,
                                        onChange: (e)=>setPendingFilters((prev)=>({
                                                    ...prev,
                                                    status: e.target.value
                                                })),
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "todos",
                                                children: "Todos"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 282,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "ativos",
                                                children: "Ativos"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 283,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "pausados",
                                                children: "Pausados"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 284,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                        lineNumber: 277,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 275,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                className: "flex flex-col text-sm",
                                children: [
                                    "Dia da semana",
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                        className: "mt-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text",
                                        value: pendingFilters.dia,
                                        onChange: (e)=>setPendingFilters((prev)=>({
                                                    ...prev,
                                                    dia: e.target.value
                                                })),
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "",
                                                children: "Todos"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 294,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "seg",
                                                children: "Seg"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 295,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "ter",
                                                children: "Ter"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 296,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "qua",
                                                children: "Qua"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 297,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "qui",
                                                children: "Qui"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 298,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "sex",
                                                children: "Sex"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 299,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "sab",
                                                children: "Sáb"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 300,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "dom",
                                                children: "Dom"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 301,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                        lineNumber: 289,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 287,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "flex items-end gap-3",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        type: "submit",
                                        className: "flex-1 rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-slate-900 shadow hover:bg-cyan-300",
                                        children: "Aplicar filtros"
                                    }, void 0, false, {
                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                        lineNumber: 305,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        type: "button",
                                        onClick: handleResetFilters,
                                        className: "rounded-xl border border-border px-4 py-2 text-sm text-text hover:text-accent",
                                        children: "Limpar"
                                    }, void 0, false, {
                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                        lineNumber: 311,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 304,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                        lineNumber: 243,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                lineNumber: 233,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("section", {
                className: "rounded-2xl border border-border/70 bg-surface/80 p-4 shadow-panel",
                children: [
                    error && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "mb-4 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200",
                        children: error
                    }, void 0, false, {
                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                        lineNumber: 325,
                        columnNumber: 11
                    }, this),
                    loading ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "animate-pulse rounded-xl border border-border/60 bg-surfaceMuted/40 p-6 text-center text-textMuted",
                        children: "Carregando agendamentos..."
                    }, void 0, false, {
                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                        lineNumber: 330,
                        columnNumber: 11
                    }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "overflow-x-auto",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("table", {
                            className: "w-full min-w-[680px] border-collapse text-sm text-text",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("thead", {
                                    className: "bg-surfaceMuted/60 text-xs uppercase tracking-wide text-textMuted",
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                className: "px-3 py-2 text-left",
                                                children: "Grupo"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 338,
                                                columnNumber: 19
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                className: "px-3 py-2 text-left",
                                                children: "CR"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 339,
                                                columnNumber: 19
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                className: "px-3 py-2 text-left",
                                                children: "Tipo"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 340,
                                                columnNumber: 19
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                className: "px-3 py-2 text-left",
                                                children: "Dias"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 341,
                                                columnNumber: 19
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                className: "px-3 py-2 text-left",
                                                children: "Janela"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 342,
                                                columnNumber: 19
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                className: "px-3 py-2 text-left",
                                                children: "Próximo envio"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 343,
                                                columnNumber: 19
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                className: "px-3 py-2 text-left",
                                                children: "Status"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 344,
                                                columnNumber: 19
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                className: "px-3 py-2 text-left",
                                                children: "Último envio"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 345,
                                                columnNumber: 19
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                className: "px-3 py-2 text-center",
                                                children: "Ações"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 346,
                                                columnNumber: 19
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                        lineNumber: 337,
                                        columnNumber: 17
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                    lineNumber: 336,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("tbody", {
                                    children: [
                                        agendamentos.map((item)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                                className: "border-b border-border/40 text-sm",
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                        className: "px-3 py-2 font-medium text-white",
                                                        children: item.nome_grupo
                                                    }, void 0, false, {
                                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                        lineNumber: 352,
                                                        columnNumber: 21
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                        className: "px-3 py-2 text-textMuted",
                                                        children: item.cr ?? "--"
                                                    }, void 0, false, {
                                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                        lineNumber: 353,
                                                        columnNumber: 21
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                        className: "px-3 py-2 capitalize",
                                                        children: item.tipo_envio
                                                    }, void 0, false, {
                                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                        lineNumber: 354,
                                                        columnNumber: 21
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                        className: "px-3 py-2 text-textMuted",
                                                        children: item.dias_semana ? item.dias_semana.split(",").map((d)=>d.trim()).join(", ") : "--"
                                                    }, void 0, false, {
                                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                        lineNumber: 355,
                                                        columnNumber: 21
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                        className: "px-3 py-2 text-textMuted",
                                                        children: [
                                                            item.hora_inicio?.slice(0, 5),
                                                            " / ",
                                                            item.hora_fim?.slice(0, 5)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                        lineNumber: 358,
                                                        columnNumber: 21
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                        className: "px-3 py-2 text-textMuted",
                                                        children: item.proximo_envio ?? "--"
                                                    }, void 0, false, {
                                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                        lineNumber: 361,
                                                        columnNumber: 21
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                        className: "px-3 py-2",
                                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            className: `rounded-full px-2 py-1 text-xs font-semibold ${item.ativo ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-200"}`,
                                                            children: item.ativo ? "Ativo" : "Pausado"
                                                        }, void 0, false, {
                                                            fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                            lineNumber: 363,
                                                            columnNumber: 23
                                                        }, this)
                                                    }, void 0, false, {
                                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                        lineNumber: 362,
                                                        columnNumber: 21
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                        className: "px-3 py-2 text-textMuted",
                                                        children: item.ultimo_status ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            children: [
                                                                item.ultimo_status,
                                                                " ",
                                                                item.ultimo_envio && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                    className: "text-xs text-textMuted/70",
                                                                    children: [
                                                                        "(",
                                                                        item.ultimo_envio,
                                                                        ")"
                                                                    ]
                                                                }, void 0, true, {
                                                                    fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                                    lineNumber: 375,
                                                                    columnNumber: 49
                                                                }, this)
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                            lineNumber: 373,
                                                            columnNumber: 25
                                                        }, this) : "--"
                                                    }, void 0, false, {
                                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                        lineNumber: 371,
                                                        columnNumber: 21
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                        className: "px-3 py-2",
                                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            className: "flex items-center justify-center gap-2 text-xs",
                                                            children: [
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                    className: "text-accent hover:underline",
                                                                    onClick: ()=>openEditModal(item),
                                                                    children: "Editar"
                                                                }, void 0, false, {
                                                                    fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                                    lineNumber: 383,
                                                                    columnNumber: 25
                                                                }, this),
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                    className: "text-accent hover:underline",
                                                                    onClick: ()=>handleClone(item),
                                                                    children: "Clonar"
                                                                }, void 0, false, {
                                                                    fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                                    lineNumber: 386,
                                                                    columnNumber: 25
                                                                }, this),
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                    className: "text-accent hover:underline",
                                                                    onClick: ()=>handleToggleStatus(item),
                                                                    children: item.ativo ? "Pausar" : "Retomar"
                                                                }, void 0, false, {
                                                                    fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                                    lineNumber: 389,
                                                                    columnNumber: 25
                                                                }, this),
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                    className: "text-accent hover:underline",
                                                                    onClick: ()=>openLogs(item),
                                                                    children: "Logs"
                                                                }, void 0, false, {
                                                                    fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                                    lineNumber: 392,
                                                                    columnNumber: 25
                                                                }, this),
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                    className: "text-rose-300 hover:underline",
                                                                    onClick: ()=>handleDelete(item),
                                                                    children: "Excluir"
                                                                }, void 0, false, {
                                                                    fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                                    lineNumber: 395,
                                                                    columnNumber: 25
                                                                }, this)
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                            lineNumber: 382,
                                                            columnNumber: 23
                                                        }, this)
                                                    }, void 0, false, {
                                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                        lineNumber: 381,
                                                        columnNumber: 21
                                                    }, this)
                                                ]
                                            }, item.id, true, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 351,
                                                columnNumber: 19
                                            }, this)),
                                        !agendamentos.length && !loading && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                className: "px-3 py-6 text-center text-textMuted",
                                                colSpan: 9,
                                                children: "Nenhum agendamento encontrado com os filtros atuais."
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                                lineNumber: 404,
                                                columnNumber: 21
                                            }, this)
                                        }, void 0, false, {
                                            fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                            lineNumber: 403,
                                            columnNumber: 19
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                    lineNumber: 349,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                            lineNumber: 335,
                            columnNumber: 13
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                        lineNumber: 334,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                lineNumber: 323,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex flex-wrap items-center justify-between gap-3 text-sm text-textMuted",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        children: [
                            "Página ",
                            page,
                            " de ",
                            totalPages,
                            " • ",
                            total,
                            " registros"
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                        lineNumber: 416,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex items-center gap-2",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                disabled: page <= 1,
                                onClick: ()=>setPage((prev)=>Math.max(1, prev - 1)),
                                className: "rounded-lg border border-border px-3 py-1 text-text disabled:opacity-40",
                                children: "Anterior"
                            }, void 0, false, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 420,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                disabled: page >= totalPages,
                                onClick: ()=>setPage((prev)=>Math.min(totalPages, prev + 1)),
                                className: "rounded-lg border border-border px-3 py-1 text-text disabled:opacity-40",
                                children: "Próxima"
                            }, void 0, false, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 428,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                value: pageSize,
                                onChange: (e)=>{
                                    setPageSize(Number(e.target.value));
                                    setPage(1);
                                },
                                className: "rounded-lg border border-border bg-surface px-2 py-1 text-text",
                                children: [
                                    10,
                                    20,
                                    50
                                ].map((size)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                        value: size,
                                        children: [
                                            size,
                                            "/página"
                                        ]
                                    }, size, true, {
                                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                        lineNumber: 445,
                                        columnNumber: 15
                                    }, this))
                            }, void 0, false, {
                                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                                lineNumber: 436,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                        lineNumber: 419,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                lineNumber: 415,
                columnNumber: 7
            }, this),
            modal.open && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$components$2f$envio$2d$sla$2f$AgendamentoModal$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                mode: modal.mode,
                agendamento: modal.agendamento ?? undefined,
                onClose: closeModal,
                onSaved: (message)=>{
                    closeModal();
                    refresh(message);
                }
            }, void 0, false, {
                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                lineNumber: 454,
                columnNumber: 9
            }, this),
            logsState.open && logsState.agendamento && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(LogsModal, {
                agendamento: logsState.agendamento,
                onClose: closeLogs
            }, void 0, false, {
                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                lineNumber: 466,
                columnNumber: 9
            }, this),
            templateState.confirm && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(ConfirmModal, {
                title: "Alterar template?",
                description: "Atualizar o template afetará todos os agendamentos já existentes. Deseja continuar?",
                confirmLabel: "Sim, editar template",
                cancelLabel: "Cancelar",
                onConfirm: openTemplateModal,
                onCancel: closeTemplateConfirm
            }, void 0, false, {
                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                lineNumber: 470,
                columnNumber: 9
            }, this),
            templateState.open && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(TemplateModal, {
                template: templateState.data,
                loading: templateState.loading,
                saving: templateState.saving,
                error: templateState.error,
                variables: __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$components$2f$envio$2d$sla$2f$constants$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["templateVariables"],
                onRetry: ensureTemplateLoaded,
                onClose: closeTemplateModal,
                onSave: handleTemplateSave
            }, void 0, false, {
                fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
                lineNumber: 481,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/frontend/components/envio-sla/EnvioSlaView.tsx",
        lineNumber: 202,
        columnNumber: 5
    }, this);
}
}),
];

//# sourceMappingURL=frontend_8aff378f._.js.map