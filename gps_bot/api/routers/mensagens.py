from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.models.mensagem import (
    atualizar_mensagem,
    criar_mensagem,
    deletar_mensagem,
    listar_mensagens,
    obter_mensagem,
    toggle_ativa,
)
from api.schemas.mensagens import (
    Mensagem,
    MensagemCreate,
    MensagemToggleResponse,
    MensagemUpdate,
)

router = APIRouter()


def _serialize_mensagem(row: tuple[Any, ...]) -> Mensagem:
    keys = [
        "id",
        "mensagem",
        "grupos_selecionados",
        "tipo_recorrencia",
        "dias_semana",
        "horario",
        "data_inicio",
        "data_fim",
        "ativo",
        "criado_em",
        "atualizado_em",
    ]
    data: Dict[str, Any] = dict(zip(keys, row))
    grupos = list(data.get("grupos_selecionados") or [])
    dias_semana = list(data.get("dias_semana") or []) or None
    return Mensagem(
        id=data["id"],
        mensagem=data["mensagem"],
        grupos_ids=grupos,
        tipo_recorrencia=data["tipo_recorrencia"],
        dias_semana=dias_semana,
        horario=data["horario"],
        data_inicio=data["data_inicio"],
        data_fim=data.get("data_fim"),
        ativo=data["ativo"],
        criado_em=data["criado_em"],
        atualizado_em=data.get("atualizado_em"),
    )


def _get_mensagem_or_404(mensagem_id: int) -> tuple[Any, ...]:
    mensagem = obter_mensagem(mensagem_id)
    if not mensagem:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    return mensagem


@router.get("/", response_model=list[Mensagem])
def listar_mensagens_endpoint(
    ativo: Optional[bool] = Query(None, description="Filtra mensagens ativas/inativas"),
) -> list[Mensagem]:
    registros = listar_mensagens(apenas_ativas=ativo)
    return [_serialize_mensagem(row) for row in registros]


@router.get("/{mensagem_id}", response_model=Mensagem)
def obter_mensagem_endpoint(mensagem_id: int) -> Mensagem:
    return _serialize_mensagem(_get_mensagem_or_404(mensagem_id))


@router.post("/", response_model=Mensagem, status_code=status.HTTP_201_CREATED)
def criar_mensagem_endpoint(payload: MensagemCreate) -> Mensagem:
    dados = payload.dict()
    nova_id = criar_mensagem(dados)
    registro = _get_mensagem_or_404(nova_id)
    return _serialize_mensagem(registro)


@router.put("/{mensagem_id}", response_model=Mensagem)
def atualizar_mensagem_endpoint(mensagem_id: int, payload: MensagemUpdate) -> Mensagem:
    dados = payload.dict()
    atualizar_mensagem(mensagem_id, dados)
    registro = _get_mensagem_or_404(mensagem_id)
    return _serialize_mensagem(registro)


@router.delete("/{mensagem_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def deletar_mensagem_endpoint(mensagem_id: int) -> Response:
    deletar_mensagem(mensagem_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{mensagem_id}/toggle", response_model=MensagemToggleResponse)
def toggle_mensagem_endpoint(mensagem_id: int) -> MensagemToggleResponse:
    novo_status = toggle_ativa(mensagem_id)
    return MensagemToggleResponse(id=mensagem_id, ativo=novo_status)
