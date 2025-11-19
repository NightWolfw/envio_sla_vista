from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Response

from api.schemas.agendamentos import (
    Agendamento,
    AgendamentoCreate,
    AgendamentoCreatedResponse,
    AgendamentoDetail,
    AgendamentoLog,
    AgendamentoLogList,
    AgendamentoListResponse,
    AgendamentoUpdate,
    EnviarAgoraResponse,
    PdfLinkResponse,
    PdfBulkResponse,
    ToggleResponse,
    BulkIdsRequest,
    BulkDeleteResponse,
)
from app.models.agendamento import (
    atualizar_agendamento,
    clonar_agendamento,
    criar_agendamento,
    deletar_agendamento,
    definir_status_agendamento,
    listar_agendamentos_filtrado,
    obter_agendamento,
    obter_logs_agendamento,
    toggle_agendamento,
)
from app.services.scheduler_service import enviar_agendamento_imediato, gerar_pdf_agendamento

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


@router.get("/", response_model=AgendamentoListResponse)
def listar_agendamentos_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    tipo_envio: str | None = Query(None),
    ativo: bool | None = Query(None),
    grupo: str | None = Query(None),
    cr: str | None = Query(None),
    dia: str | None = Query(None),
    data_inicio: datetime | None = Query(None),
    data_fim: datetime | None = Query(None),
) -> AgendamentoListResponse:
    filtros = {
        "tipo_envio": tipo_envio,
        "ativo": ativo,
        "grupo": grupo,
        "cr": cr,
        "dia": dia,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
    }
    itens, total = listar_agendamentos_filtrado(filtros, page, page_size)
    return AgendamentoListResponse(
        items=[Agendamento(**item) for item in itens],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=AgendamentoCreatedResponse, status_code=201)
def criar_agendamento_endpoint(payload: AgendamentoCreate) -> AgendamentoCreatedResponse:
    dados = payload.dict()
    dados["dias_semana"] = ",".join(payload.dias_semana)
    agendamento_id = criar_agendamento(dados)
    return AgendamentoCreatedResponse(id=agendamento_id)


@router.post("/bulk/pdf", response_model=PdfBulkResponse)
def gerar_pdf_em_massa(payload: BulkIdsRequest) -> PdfBulkResponse:
    successes: list[PdfLinkResponse] = []
    failures: list[int] = []
    for agendamento_id in payload.ids:
        try:
            url = gerar_pdf_agendamento(agendamento_id)
            successes.append(PdfLinkResponse(id=agendamento_id, url=url))
        except LookupError:
            failures.append(agendamento_id)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    return PdfBulkResponse(successes=successes, failures=failures)


@router.delete("/bulk", response_model=BulkDeleteResponse)
def deletar_agendamentos_em_massa(payload: BulkIdsRequest) -> BulkDeleteResponse:
    removidos = 0
    failures: list[int] = []
    for agendamento_id in payload.ids:
        try:
            deletar_agendamento(agendamento_id)
            removidos += 1
        except Exception:
            failures.append(agendamento_id)
    return BulkDeleteResponse(removed=removidos, failures=failures)


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


@router.post("/{agendamento_id}/clone", response_model=AgendamentoCreatedResponse, status_code=201)
def clonar_agendamento_endpoint(agendamento_id: int) -> AgendamentoCreatedResponse:
    novo_id = clonar_agendamento(agendamento_id)
    return AgendamentoCreatedResponse(id=novo_id)


@router.post("/{agendamento_id}/pause", response_model=ToggleResponse)
def pausar_agendamento_endpoint(agendamento_id: int) -> ToggleResponse:
    definir_status_agendamento(agendamento_id, False)
    registro = obter_agendamento(agendamento_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado após pausa")
    detalhe = _serialize_agendamento_detail(registro)
    return ToggleResponse(id=detalhe.id, ativo=detalhe.ativo)


@router.post("/{agendamento_id}/resume", response_model=ToggleResponse)
def retomar_agendamento_endpoint(agendamento_id: int) -> ToggleResponse:
    definir_status_agendamento(agendamento_id, True)
    registro = obter_agendamento(agendamento_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado após retomada")
    detalhe = _serialize_agendamento_detail(registro)
    return ToggleResponse(id=detalhe.id, ativo=detalhe.ativo)


@router.post("/{agendamento_id}/send-now", response_model=EnviarAgoraResponse)
def enviar_agora_endpoint(agendamento_id: int) -> EnviarAgoraResponse:
    try:
        agendamento = enviar_agendamento_imediato(agendamento_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return EnviarAgoraResponse(id=agendamento["id"], status="enviado", message="Envio manual concluído com sucesso.")



@router.post("/{agendamento_id}/pdf", response_model=PdfLinkResponse)
def gerar_pdf_agendamento_endpoint(agendamento_id: int) -> PdfLinkResponse:
    try:
        url = gerar_pdf_agendamento(agendamento_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return PdfLinkResponse(id=agendamento_id, url=url)


@router.get("/{agendamento_id}/logs", response_model=AgendamentoLogList)
def listar_logs_agendamento_endpoint(
    agendamento_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
) -> AgendamentoLogList:
    logs, total = obter_logs_agendamento(agendamento_id, page, page_size)
    return AgendamentoLogList(
        items=[AgendamentoLog(**log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
    )
