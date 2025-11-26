from __future__ import annotations

import calendar
import logging
import threading
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
from app.services.dashboard_etl import carregar_mes_corrente

TIMEZONE_BRASILIA = pytz.timezone("America/Sao_Paulo")

router = APIRouter()
logger = logging.getLogger(__name__)

_sync_lock = threading.Lock()
_sync_running = False


def _run_sync_background(filtros: Dict[str, str]) -> None:
    global _sync_running
    try:
        logger.info("[Dashboard] Sync background iniciada para filtros: %s", filtros)
        atualizar_dashboard_cache(filtros)
        logger.info("[Dashboard] Sync background concluída para filtros: %s", filtros)
    except Exception as exc:  # noqa: BLE001
        logger.error("[Dashboard] Sync background falhou: %s", exc)
    finally:
        with _sync_lock:
            _sync_running = False


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
def dashboard_sla_cached(
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
    """
    Retorna o dashboard (cache Redis). Se não houver cache, NÃO gera dados novos.
    """
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
    cached = get_cached_dashboard(filtros)
    if not cached:
        return {"success": False, "cached": False, "last_updated": None, "data": None, "reason": "no_cache"}
    return {"success": True, "cached": True, "last_updated": cached.get("last_updated"), "data": cached}


@router.post("/sla/sync")
def dashboard_sla_sync(
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
    """
    Sincronização manual agora é assíncrona: dispara atualização em background e retorna rápido.
    Se já houver cache, devolve o cache atual para evitar 504/timeout.
    """
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
    cached = get_cached_dashboard(filtros)

    # Dispara em background se não estiver rodando
    started = False
    global _sync_running  # noqa: PLW0603
    with _sync_lock:
        if not _sync_running:
            _sync_running = True
            started = True
            t = threading.Thread(target=_run_sync_background, args=(filtros,), daemon=True)
            t.start()

    if started:
        logger.info("[Dashboard] Sync manual disparada em background (daemon) para filtros: %s", filtros)
    else:
        logger.info("[Dashboard] Sync manual ignorada porque já existe uma em execução (filtros: %s)", filtros)

    # Se já existe cache, devolve imediatamente para evitar 504; senão retorna com data=None
    return {
        "success": True,
        "cached": bool(cached),
        "last_updated": cached.get("last_updated") if cached else None,
        "data": cached,
        "sync_running": True,
        "sync_started": started,
    }


@router.get("/sla/config")
def dashboard_config_get() -> Dict[str, Any]:
    config = obter_config_dashboard()
    return {"success": True, "data": config}


@router.put("/sla/config")
def dashboard_config_put(
    intervalo_minutos: int = Body(10, embed=True),
    monitor_ativo: bool = Body(False, embed=True),
) -> Dict[str, Any]:
    if intervalo_minutos <= 0:
        raise HTTPException(status_code=400, detail="intervalo_minutos deve ser > 0")
    data = salvar_config_dashboard(intervalo_minutos, monitor_ativo)
    # Limpa cache para forçar regeneração conforme nova config
    clear_cached_dashboard()
    return {"success": True, "data": data}
