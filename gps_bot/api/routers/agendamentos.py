from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Response

from api.schemas.agendamentos import (
    Agendamento,
    AgendamentoCreate,
    AgendamentoCreatedResponse,
    AgendamentoDetail,
    AgendamentoLog,
    AgendamentoUpdate,
    ToggleResponse,
)
from app.models.agendamento import (
    atualizar_agendamento,
    criar_agendamento,
    deletar_agendamento,
    listar_agendamentos,
    obter_agendamento,
    obter_logs_agendamento,
    toggle_agendamento,
)

router = APIRouter()


def _serialize_agendamento_detail(row: tuple[Any, ...]) -> AgendamentoDetail:
    keys = [
        "id",
        "grupo_id",
        "tipo_envio",
        "dias_semana",
        "data_envio",
        "hora_inicio",
        "dia_offset_inicio",
        "hora_fim",
        "dia_offset_fim",
        "ativo",
        "proximo_envio",
        "criado_em",
        "atualizado_em",
    ]
    data = dict(zip(keys, row))
    return AgendamentoDetail(
        id=data["id"],
        grupo_id=data["grupo_id"],
        tipo_envio=data["tipo_envio"],
        dias_semana=data.get("dias_semana"),
        data_envio=data["data_envio"],
        hora_inicio=data["hora_inicio"],
        dia_offset_inicio=data["dia_offset_inicio"],
        hora_fim=data["hora_fim"],
        dia_offset_fim=data["dia_offset_fim"],
        ativo=data["ativo"],
        proximo_envio=data.get("proximo_envio"),
        criado_em=data["criado_em"],
        atualizado_em=data.get("atualizado_em"),
    )


@router.get("/", response_model=list[Agendamento])
def listar_agendamentos_endpoint() -> list[Agendamento]:
    agendamentos = listar_agendamentos()
    return [Agendamento(**agendamento) for agendamento in agendamentos]


@router.post("/", response_model=AgendamentoCreatedResponse, status_code=201)
def criar_agendamento_endpoint(payload: AgendamentoCreate) -> AgendamentoCreatedResponse:
    dados = payload.dict()
    dados["dias_semana"] = ",".join(payload.dias_semana)
    agendamento_id = criar_agendamento(dados)
    return AgendamentoCreatedResponse(id=agendamento_id)


@router.get("/{agendamento_id}", response_model=AgendamentoDetail)
def obter_agendamento_endpoint(agendamento_id: int) -> AgendamentoDetail:
    registro = obter_agendamento(agendamento_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return _serialize_agendamento_detail(registro)


@router.put("/{agendamento_id}", response_model=AgendamentoDetail)
def atualizar_agendamento_endpoint(agendamento_id: int, payload: AgendamentoUpdate) -> AgendamentoDetail:
    dados = payload.dict()
    dados["dias_semana"] = ",".join(payload.dias_semana)
    atualizar_agendamento(agendamento_id, dados)
    registro = obter_agendamento(agendamento_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado após atualização")
    return _serialize_agendamento_detail(registro)


@router.delete("/{agendamento_id}", status_code=204, response_class=Response)
def deletar_agendamento_endpoint(agendamento_id: int) -> Response:
    deletar_agendamento(agendamento_id)
    return Response(status_code=204)


@router.post("/{agendamento_id}/toggle", response_model=ToggleResponse)
def toggle_agendamento_endpoint(agendamento_id: int) -> ToggleResponse:
    toggle_agendamento(agendamento_id)
    registro = obter_agendamento(agendamento_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado após toggle")
    detalhe = _serialize_agendamento_detail(registro)
    return ToggleResponse(id=detalhe.id, ativo=detalhe.ativo)


@router.get("/{agendamento_id}/logs", response_model=list[AgendamentoLog])
def listar_logs_agendamento_endpoint(agendamento_id: int) -> list[AgendamentoLog]:
    logs = obter_logs_agendamento(agendamento_id)
    return [AgendamentoLog(**log) for log in logs]
