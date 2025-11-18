from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from api.schemas import (
    EvolutionGroup,
    EvolutionGroupsResponse,
    EvolutionImportRequest,
    EvolutionImportResponse,
)
from app.services import whatsapp_sync

router = APIRouter()


@router.get("/groups", response_model=EvolutionGroupsResponse)
def listar_grupos_evolution(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    force_refresh: bool = Query(False)
):
    try:
        grupos = whatsapp_sync.comparar_grupos_novos(force_refresh=force_refresh)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erro ao consultar Evolution API: {exc}") from exc

    total = len(grupos)
    start = (page - 1) * page_size
    end = start + page_size
    slice_items = grupos[start:end]
    items = [EvolutionGroup(group_id=g["group_id"], nome=g["nome"]) for g in slice_items]

    return EvolutionGroupsResponse(total=total, page=page, page_size=page_size, grupos=items)


@router.get("/groups/all", response_model=EvolutionGroupsResponse)
def listar_todos_grupos_evolution(force_refresh: bool = Query(False)):
    try:
        grupos = whatsapp_sync.comparar_grupos_novos(force_refresh=force_refresh)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erro ao consultar Evolution API: {exc}") from exc

    total = len(grupos)
    items = [EvolutionGroup(group_id=g["group_id"], nome=g["nome"]) for g in grupos]

    return EvolutionGroupsResponse(total=total, page=1, page_size=max(total, 1), grupos=items)


@router.post("/import", response_model=EvolutionImportResponse)
def importar_grupos(payload: EvolutionImportRequest):
    try:
        result = whatsapp_sync.inserir_grupos_novos([group.dict() for group in payload.grupos])
        return EvolutionImportResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao inserir grupos: {exc}") from exc
