from __future__ import annotations

import calendar
from datetime import datetime, timedelta
import pytz
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi import Body

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
from app.models.dashboard_config import obter_config_dashboard, salvar_config_dashboard
from app.services.dashboard_cache import get_cached_dashboard, set_cached_dashboard, clear_cached_dashboard
from app.services.dashboard_refresh import atualizar_dashboard_cache

TIMEZONE_BRASILIA = pytz.timezone("America/Sao_Paulo")

router = APIRouter()


def _collect_filtros(**params: Optional[str]) -> Dict[str, str]:
    """Remove valores vazios dos filtros."""
    return {k: v for k, v in params.items() if v}


def _ensure_default_diretor(filtros: Dict[str, str]) -> Dict[str, str]:
    """Garante que sempre temos um diretor executivo padrão."""
    if "diretor_executivo" not in filtros:
        filtros["diretor_executivo"] = "MARCOS NASCIMENTO PEDREIRA"
    return filtros


def _mes_ano_defaults(mes: Optional[int], ano: Optional[int]) -> tuple[int, int]:
    hoje = datetime.now(TIMEZONE_BRASILIA)
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
    filtros = _ensure_default_diretor(
        _collect_filtros(
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
    )

    hoje = datetime.now(TIMEZONE_BRASILIA)
    primeiro_dia = hoje.replace(hour=0, minute=0, second=0, microsecond=0)
    ultimo_dia = primeiro_dia + timedelta(days=1) - timedelta(microseconds=1)

    stats = buscar_resumo_tarefas(filtros, primeiro_dia, ultimo_dia)
    return {
        "success": True,
        "data": stats,
        "periodo": {
            "inicio": primeiro_dia.isoformat(),
            "fim": ultimo_dia.isoformat(),
            "descricao": primeiro_dia.strftime("%d/%m/%Y"),
            "label": f"Resultados do dia {primeiro_dia.strftime('%d/%m/%Y')}"
        },
    }


@router.get("/tarefas-mes")
def dashboard_tarefas_mes(
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
    target_mes, target_ano = _mes_ano_defaults(mes, ano)
    filtros = _ensure_default_diretor(
        _collect_filtros(
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
    )
    dados = buscar_tarefas_por_dia_mes(filtros, target_mes, target_ano)
    return {"success": True, "data": dados}


@router.get("/heatmap")
def dashboard_heatmap(
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
    target_mes, target_ano = _mes_ano_defaults(mes, ano)
    primeiro_dia = TIMEZONE_BRASILIA.localize(datetime(target_ano, target_mes, 1))
    ultimo_dia = TIMEZONE_BRASILIA.localize(
        datetime(
            target_ano,
            target_mes,
            calendar.monthrange(target_ano, target_mes)[1],
            23,
            59,
            59,
        )
    )
    filtros = _ensure_default_diretor(
        _collect_filtros(
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
    )
    dados = buscar_heatmap_realizacao(filtros, primeiro_dia, ultimo_dia)
    return {"success": True, "data": dados}


@router.get("/executores")
def dashboard_executores(
    limit: int = Query(10, ge=1, le=100),
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
    target_mes, target_ano = _mes_ano_defaults(mes, ano)
    primeiro_dia = TIMEZONE_BRASILIA.localize(datetime(target_ano, target_mes, 1))
    ultimo_dia = TIMEZONE_BRASILIA.localize(
        datetime(
            target_ano,
            target_mes,
            calendar.monthrange(target_ano, target_mes)[1],
            23,
            59,
            59,
        )
    )
    filtros = _ensure_default_diretor(
        _collect_filtros(
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
    )
    dados = buscar_top_executores(filtros, primeiro_dia, ultimo_dia, limit)
    return {"success": True, "data": dados}


@router.get("/locais")
def dashboard_locais(
    limit: int = Query(10, ge=1, le=100),
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
    target_mes, target_ano = _mes_ano_defaults(mes, ano)
    primeiro_dia = TIMEZONE_BRASILIA.localize(datetime(target_ano, target_mes, 1))
    ultimo_dia = TIMEZONE_BRASILIA.localize(
        datetime(
            target_ano,
            target_mes,
            calendar.monthrange(target_ano, target_mes)[1],
            23,
            59,
            59,
        )
    )
    filtros = _ensure_default_diretor(
        _collect_filtros(
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
    )
    dados = buscar_top_locais(filtros, primeiro_dia, ultimo_dia, limit)
    return {"success": True, "data": dados}


@router.get("/pizza")
def dashboard_pizza(
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
    target_mes, target_ano = _mes_ano_defaults(mes, ano)
    primeiro_dia = TIMEZONE_BRASILIA.localize(datetime(target_ano, target_mes, 1))
    ultimo_dia = TIMEZONE_BRASILIA.localize(
        datetime(
            target_ano,
            target_mes,
            calendar.monthrange(target_ano, target_mes)[1],
            23,
            59,
            59,
        )
    )
    filtros = _ensure_default_diretor(
        _collect_filtros(
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
    )
    dados = buscar_distribuicao_status(filtros, primeiro_dia, ultimo_dia)
    return {"success": True, "data": dados}


@router.get("/filtros")
def dashboard_filtros() -> Dict[str, Any]:
    opcoes = buscar_opcoes_filtros()
    return {"success": True, "data": opcoes}


@router.get("/heatmap-dias")
def dashboard_heatmap_dias(
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
    target_mes, target_ano = _mes_ano_defaults(mes, ano)
    filtros = _ensure_default_diretor(
        _collect_filtros(
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
    )
    dados = buscar_heatmap_por_dia(filtros, target_mes, target_ano)
    return {"success": True, "data": dados, "mes": target_mes, "ano": target_ano}


@router.get("/supervisores-por-gerente")
def supervisores_por_gerente(gerente: Optional[str] = None) -> Dict[str, Any]:
    if not gerente:
        raise HTTPException(status_code=400, detail="Gerente não informado")
    supervisores = buscar_supervisores_por_gerente(gerente)
    return {"success": True, "data": supervisores}


@router.get("/sla")
def dashboard_sla_cached() -> Dict[str, Any]:
    """
    Retorna o dashboard (cache Redis). Se não houver cache, tenta gerar uma vez.
    """
    cached = get_cached_dashboard()
    if cached:
        return {"success": True, "cached": True, "last_updated": cached.get("last_updated"), "data": cached}
    # Gera on-demand apenas para evitar tela vazia; usa diretor padrão
    data = atualizar_dashboard_cache({})
    return {"success": True, "cached": False, "last_updated": data.get("last_updated"), "data": data}


@router.post("/sla/sync")
def dashboard_sla_sync() -> Dict[str, Any]:
    """
    Sincronização manual: força atualização agora (retorna o payload atualizado).
    """
    data = atualizar_dashboard_cache({})
    return {"success": True, "cached": False, "last_updated": data.get("last_updated"), "data": data}


@router.get("/sla/config")
def dashboard_config_get() -> Dict[str, Any]:
    config = obter_config_dashboard()
    return {"success": True, "data": config}


@router.put("/sla/config")
def dashboard_config_put(
    hora_inicio: str = Body(..., embed=True),
    hora_fim: str = Body(..., embed=True),
    intervalo_minutos: int = Body(10, embed=True),
) -> Dict[str, Any]:
    try:
        h_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
        h_fim = datetime.strptime(hora_fim, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de hora inválido. Use HH:MM.")
    if intervalo_minutos <= 0:
        raise HTTPException(status_code=400, detail="intervalo_minutos deve ser > 0")
    data = salvar_config_dashboard(h_inicio, h_fim, intervalo_minutos)
    # Limpa cache para forçar regeneração conforme nova config
    clear_cached_dashboard()
    return {"success": True, "data": data}
