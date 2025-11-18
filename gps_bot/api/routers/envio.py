from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.database import get_db_site
from app.models.grupo import listar_grupos, obter_valores_unicos_filtros
from app.services.whatsapp import enviar_mensagem

router = APIRouter()


class EnvioRequest(BaseModel):
    mensagem: str = Field(..., min_length=1)
    grupos_ids: List[str] = Field(..., min_items=1)


class EnvioDetalhe(BaseModel):
    grupo: str
    group_id: str
    sucesso: bool
    erro: str | None = None


class EnvioResponse(BaseModel):
    sucessos: int
    erros: int
    detalhes: List[EnvioDetalhe]


def _serialize_grupo(row: tuple[Any, ...]) -> Dict[str, Any]:
    return {
        "id": row[0],
        "group_id": row[1],
        "nome_grupo": row[2],
        "envio": row[3],
        "cr": row[4],
        "cliente": row[5],
        "pec_01": row[6],
        "pec_02": row[7],
        "diretorexecutivo": row[8],
        "diretorregional": row[9],
        "gerenteregional": row[10],
        "gerente": row[11],
        "supervisor": row[12],
    }


@router.get("/grupos")
def listar_grupos_para_envio() -> list[Dict[str, Any]]:
    """Retorna grupos com envio habilitado."""
    grupos = listar_grupos({"envio": True})
    return [_serialize_grupo(grupo) for grupo in grupos]


@router.get("/filtros")
def listar_filtros_envio() -> Dict[str, list[str]]:
    """Retorna filtros disponíveis (apenas ativos)."""
    return obter_valores_unicos_filtros(apenas_ativos=True)


@router.post("/processar", response_model=EnvioResponse)
def processar_envio(payload: EnvioRequest) -> EnvioResponse:
    """Envia mensagem manualmente para grupos selecionados."""
    conn = get_db_site()
    cur = conn.cursor()

    placeholders = ",".join(["%s"] * len(payload.grupos_ids))
    query = f"""
        SELECT group_id, nome_grupo
        FROM grupos_whatsapp
        WHERE group_id IN ({placeholders}) AND envio = TRUE
    """
    cur.execute(query, tuple(payload.grupos_ids))
    grupos_db = cur.fetchall()
    cur.close()
    conn.close()

    if not grupos_db:
        raise HTTPException(status_code=400, detail="Nenhum grupo ativo encontrado para envio")

    sucessos = 0
    erros = 0
    detalhes: list[EnvioDetalhe] = []

    for group_id, nome_grupo in grupos_db:
        sucesso, erro = enviar_mensagem(group_id, payload.mensagem)
        detalhes.append(
            EnvioDetalhe(
                grupo=nome_grupo,
                group_id=group_id,
                sucesso=sucesso,
                erro=erro,
            )
        )
        if sucesso:
            sucessos += 1
        else:
            erros += 1

    return EnvioResponse(sucessos=sucessos, erros=erros, detalhes=detalhes)
