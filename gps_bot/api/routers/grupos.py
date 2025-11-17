from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from gps_bot.api.schemas.grupos import Grupo, GrupoFiltersResponse, GrupoUpdate
from gps_bot.app.models.grupo import (
    listar_grupos,
    obter_grupo,
    obter_valores_unicos_filtros,
    atualizar_grupo,
)

router = APIRouter()


def _serialize_grupo(row: tuple[Any, ...]) -> Grupo:
    keys = [
        "id",
        "group_id",
        "nome_grupo",
        "envio",
        "cr",
        "cliente",
        "pec_01",
        "pec_02",
        "diretorexecutivo",
        "diretorregional",
        "gerenteregional",
        "gerente",
        "supervisor",
    ]
    data = dict(zip(keys, row))
    return Grupo(
        id=data["id"],
        group_id=data["group_id"],
        nome_grupo=data["nome_grupo"],
        envio=bool(data["envio"]),
        cr=data.get("cr"),
        cliente=data.get("cliente"),
        pec_01=data.get("pec_01"),
        pec_02=data.get("pec_02"),
        diretor_executivo=data.get("diretorexecutivo"),
        diretor_regional=data.get("diretorregional"),
        gerente_regional=data.get("gerenteregional"),
        gerente=data.get("gerente"),
        supervisor=data.get("supervisor"),
    )


@router.get("/", response_model=list[Grupo])
def listar_grupos_endpoint(
    grupo_id: Optional[int] = Query(None, description="Filtro por ID"),
    nome: Optional[str] = Query(None, description="Filtro por nome parcial"),
    cr: Optional[str] = Query(None, description="Filtro por CR"),
    envio: Optional[bool] = Query(None, description="Filtro por envio habilitado"),
    diretorexecutivo: Optional[str] = None,
    diretorregional: Optional[str] = None,
    gerenteregional: Optional[str] = None,
    gerente: Optional[str] = None,
    supervisor: Optional[str] = None,
    cliente: Optional[str] = None,
    pec_01: Optional[str] = None,
    pec_02: Optional[str] = None,
) -> list[Grupo]:
    filtros: Dict[str, Any] = {}
    params = {
        "id": grupo_id,
        "nome": nome,
        "cr": cr,
        "envio": envio,
        "diretorexecutivo": diretorexecutivo,
        "diretorregional": diretorregional,
        "gerenteregional": gerenteregional,
        "gerente": gerente,
        "supervisor": supervisor,
        "cliente": cliente,
        "pec_01": pec_01,
        "pec_02": pec_02,
    }

    for key, value in params.items():
        if value is not None:
            filtros[key] = value

    rows = listar_grupos(filtros if filtros else None)
    return [_serialize_grupo(row) for row in rows]


@router.get("/filtros/meta", response_model=GrupoFiltersResponse)
def listar_filtros() -> GrupoFiltersResponse:
    filtros = obter_valores_unicos_filtros(apenas_ativos=True)
    return GrupoFiltersResponse(**filtros)


@router.get("/{grupo_id}", response_model=Grupo)
def obter_grupo_endpoint(grupo_id: int) -> Grupo:
    grupo = obter_grupo(grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return _serialize_grupo(grupo)


@router.put("/{grupo_id}", response_model=Grupo)
def atualizar_grupo_endpoint(grupo_id: int, payload: GrupoUpdate) -> Grupo:
    atualizar_grupo(grupo_id, payload.dict())
    grupo = obter_grupo(grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado após atualização")
    return _serialize_grupo(grupo)
