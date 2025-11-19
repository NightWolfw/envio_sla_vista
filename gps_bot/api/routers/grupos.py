from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from api.schemas.grupos import (
    Grupo,
    GrupoFiltersResponse,
    GrupoUpdate,
    GrupoDeleteRequest,
    GrupoDeleteResponse,
    GrupoCRItem,
)
from app.models.grupo import (
    listar_grupos,
    obter_grupo,
    obter_valores_unicos_filtros,
    atualizar_grupo,
    listar_ids_com_cr,
    deletar_grupos_por_ids,
    GRUPO_COLUMNS,
)
from app.services.estrutura import atualizar_dados_estrutura, atualizar_grupo_especifico

router = APIRouter()


def _serialize_grupo(row: tuple[Any, ...]) -> Grupo:
    data = dict(zip(GRUPO_COLUMNS, row))
    return Grupo(
        id=data["id"],
        group_id=data["group_id"],
        nome_grupo=data["nome_grupo"],
        envio=bool(data["envio"]),
        envio_pdf=bool(data.get("envio_pdf", False)),
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


@router.get("/com-cr", response_model=list[GrupoCRItem])
def listar_com_cr() -> list[GrupoCRItem]:
    rows = listar_ids_com_cr()
    return [GrupoCRItem(id=row[0], nome_grupo=row[1], cr=row[2]) for row in rows]


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


@router.delete("/", response_model=GrupoDeleteResponse)
def deletar_grupos(payload: GrupoDeleteRequest) -> GrupoDeleteResponse:
    removidos = deletar_grupos_por_ids(payload.ids)
    return GrupoDeleteResponse(removidos=removidos)


@router.post("/{grupo_id}/sync-estrutura")
def sincronizar_grupo(grupo_id: int) -> dict[str, bool]:
    sucesso = atualizar_grupo_especifico(grupo_id)
    if not sucesso:
        raise HTTPException(status_code=400, detail="Não foi possível atualizar a estrutura deste grupo.")
    return {"success": True}


@router.post("/sync-estrutura")
def sincronizar_todos() -> dict[str, int]:
    resultado = atualizar_dados_estrutura()
    return resultado
