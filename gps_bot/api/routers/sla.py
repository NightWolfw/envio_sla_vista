from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas.sla import SLAPreview, SLAPreviewRequest
from app.models.grupo import obter_grupo
from app.services.mensagem_agendamento import (
    calcular_datas_consulta,
    formatar_mensagem_programadas,
    formatar_mensagem_resultados,
)
from app.services.sla_consulta import buscar_tarefas_por_periodo

router = APIRouter()


@router.post("/preview/{grupo_id}", response_model=SLAPreview)
def preview_mensagem(grupo_id: int, payload: SLAPreviewRequest) -> SLAPreview:
    grupo = obter_grupo(grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")

    cr = grupo[4]
    nome_grupo = grupo[2]

    if not cr:
        raise HTTPException(status_code=400, detail="Grupo sem CR configurado")

    data_inicio, data_fim = calcular_datas_consulta(
        payload.data_envio,
        payload.hora_inicio,
        payload.dia_offset_inicio,
        payload.hora_fim,
        payload.dia_offset_fim,
    )

    try:
        stats = buscar_tarefas_por_periodo(cr, data_inicio, data_fim, payload.tipo_envio)
    except Exception:
        stats = {
            "finalizadas": 0,
            "nao_realizadas": 0,
            "em_aberto": 0,
            "iniciadas": 0,
        }

    if payload.tipo_envio == "resultados":
        mensagem = formatar_mensagem_resultados(data_inicio, data_fim, stats, payload.data_envio)
    else:
        mensagem = formatar_mensagem_programadas(data_inicio, data_fim, stats, payload.data_envio)

    return SLAPreview(
        grupo_id=grupo_id,
        grupo_nome=nome_grupo,
        cr=cr,
        periodo_inicio=data_inicio,
        periodo_fim=data_fim,
        envio_agendado=payload.data_envio,
        tipo_envio=payload.tipo_envio,
        stats=stats,
        mensagem=mensagem,
    )
