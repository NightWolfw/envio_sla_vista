from __future__ import annotations

import calendar
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.dashboard import (
    buscar_distribuicao_status,
    buscar_heatmap_por_dia,
    buscar_heatmap_realizacao,
    buscar_opcoes_filtros,
    buscar_resumo_tarefas,
    buscar_supervisores_por_gerente,
    buscar_tarefas_por_dia_mes,
    buscar_top_executores,
    buscar_top_locais,
)

router = APIRouter()


def _collect_filtros(**params: Optional[str]) -> Dict[str, str]:
    """Remove valores vazios dos filtros."""
    return {k: v for k, v in params.items() if v}


def _mes_ano_defaults(mes: Optional[int], ano: Optional[int]) -> tuple[int, int]:
    hoje = datetime.now()
    return (mes or hoje.month, ano or hoje.year)


@router.get("/resumo")
def dashboard_resumo(
    mes: Optional[int] = Query(None, ge=1, le=12),
    ano: Optional[int] = Query(None, ge=2000),
    cr: Optional[str] = None,
    cliente: Optional[str] = None,
    diretor_executivo: Optional[str] = None,
    diretor_regional: Optional[str] = None,
    gerente_regional: Optional[str] = None,
    gerente: Optional[str] = None,
    supervisor: Optional[str] = None,
    pec_01: Optional[str] = None,
    pec_02: Optional[str] = None,
) -> Dict[str, Any]:
    filtros = _collect_filtros(
        cr=cr,
        cliente=cliente,
        diretor_executivo=diretor_executivo,
        diretor_regional=diretor_regional,
        gerente_regional=gerente_regional,
        gerente=gerente,
        supervisor=supervisor,
        pec_01=pec_01,
        pec_02=pec_02,
    )

    target_mes, target_ano = _mes_ano_defaults(mes, ano)
    primeiro_dia = datetime(target_ano, target_mes, 1)
    ultimo_dia = datetime(
        target_ano,
        target_mes,
        calendar.monthrange(target_ano, target_mes)[1],
        23,
        59,
        59,
    )

    stats = buscar_resumo_tarefas(filtros, primeiro_dia, ultimo_dia)
    return {
        "success": True,
        "data": stats,
        "periodo": {
            "mes": target_mes,
            "ano": target_ano,
            "mes_nome": calendar.month_name[target_mes],
        },
    }


@router.get("/tarefas-mes")
def dashboard_tarefas_mes(
    mes: Optional[int] = Query(None, ge=1, le=12),
    ano: Optional[int] = Query(None, ge=2000),
    **filtros: str,
) -> Dict[str, Any]:
    target_mes, target_ano = _mes_ano_defaults(mes, ano)
    dados = buscar_tarefas_por_dia_mes(_collect_filtros(**filtros), target_mes, target_ano)
    return {"success": True, "data": dados}


@router.get("/heatmap")
def dashboard_heatmap(
    mes: Optional[int] = Query(None, ge=1, le=12),
    ano: Optional[int] = Query(None, ge=2000),
    **filtros: str,
) -> Dict[str, Any]:
    target_mes, target_ano = _mes_ano_defaults(mes, ano)
    primeiro_dia = datetime(target_ano, target_mes, 1)
    ultimo_dia = datetime(
        target_ano,
        target_mes,
        calendar.monthrange(target_ano, target_mes)[1],
        23,
        59,
        59,
    )
    dados = buscar_heatmap_realizacao(_collect_filtros(**filtros), primeiro_dia, ultimo_dia)
    return {"success": True, "data": dados}


@router.get("/executores")
def dashboard_executores(
    limit: int = Query(10, ge=1, le=100),
    mes: Optional[int] = Query(None, ge=1, le=12),
    ano: Optional[int] = Query(None, ge=2000),
    **filtros: str,
) -> Dict[str, Any]:
    target_mes, target_ano = _mes_ano_defaults(mes, ano)
    primeiro_dia = datetime(target_ano, target_mes, 1)
    ultimo_dia = datetime(
        target_ano,
        target_mes,
        calendar.monthrange(target_ano, target_mes)[1],
        23,
        59,
        59,
    )
    dados = buscar_top_executores(_collect_filtros(**filtros), primeiro_dia, ultimo_dia, limit)
    return {"success": True, "data": dados}


@router.get("/locais")
def dashboard_locais(
    limit: int = Query(10, ge=1, le=100),
    mes: Optional[int] = Query(None, ge=1, le=12),
    ano: Optional[int] = Query(None, ge=2000),
    **filtros: str,
) -> Dict[str, Any]:
    target_mes, target_ano = _mes_ano_defaults(mes, ano)
    primeiro_dia = datetime(target_ano, target_mes, 1)
    ultimo_dia = datetime(
        target_ano,
        target_mes,
        calendar.monthrange(target_ano, target_mes)[1],
        23,
        59,
        59,
    )
    dados = buscar_top_locais(_collect_filtros(**filtros), primeiro_dia, ultimo_dia, limit)
    return {"success": True, "data": dados}


@router.get("/pizza")
def dashboard_pizza(
    mes: Optional[int] = Query(None, ge=1, le=12),
    ano: Optional[int] = Query(None, ge=2000),
    **filtros: str,
) -> Dict[str, Any]:
    target_mes, target_ano = _mes_ano_defaults(mes, ano)
    primeiro_dia = datetime(target_ano, target_mes, 1)
    ultimo_dia = datetime(
        target_ano,
        target_mes,
        calendar.monthrange(target_ano, target_mes)[1],
        23,
        59,
        59,
    )
    dados = buscar_distribuicao_status(_collect_filtros(**filtros), primeiro_dia, ultimo_dia)
    return {"success": True, "data": dados}


@router.get("/filtros")
def dashboard_filtros() -> Dict[str, Any]:
    opcoes = buscar_opcoes_filtros()
    return {"success": True, "data": opcoes}


@router.get("/heatmap-dias")
def dashboard_heatmap_dias(
    mes: Optional[int] = Query(None, ge=1, le=12),
    ano: Optional[int] = Query(None, ge=2000),
    **filtros: str,
) -> Dict[str, Any]:
    target_mes, target_ano = _mes_ano_defaults(mes, ano)
    dados = buscar_heatmap_por_dia(_collect_filtros(**filtros), target_mes, target_ano)
    return {"success": True, "data": dados, "mes": target_mes, "ano": target_ano}


@router.get("/supervisores-por-gerente")
def supervisores_por_gerente(gerente: Optional[str] = None) -> Dict[str, Any]:
    if not gerente:
        raise HTTPException(status_code=400, detail="Gerente não informado")
    supervisores = buscar_supervisores_por_gerente(gerente)
    return {"success": True, "data": supervisores}
