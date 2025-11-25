from __future__ import annotations

import calendar
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytz

from app.models.database import get_db_vista
from app.models.dashboard import buscar_opcoes_filtros
from app.services.dashboard_cache import set_cached_dashboard
from config import DB_CONFIG

logger = logging.getLogger(__name__)
TIMEZONE_BRASILIA = pytz.timezone("America/Sao_Paulo")


def _coerce_filters(filtros: Dict[str, Optional[str]]) -> Dict[str, str]:
    base = {k: v for k, v in filtros.items() if v}
    if "diretor_executivo" not in base:
        base["diretor_executivo"] = "MARCOS NASCIMENTO PEDREIRA"
    return base


def _where_and_params(filtros: Dict[str, str], start: datetime, end: datetime) -> tuple[str, List[Any], str]:
    clauses = ["t.disponibilizacao >= %s", "t.disponibilizacao <= %s"]
    params: List[Any] = [start, end]
    join_cr = ""
    filtros_gestores = []

    if filtros.get("cr"):
        clauses.append("e.crno = %s")
        params.append(filtros["cr"])
    if filtros.get("cliente"):
        clauses.append("e.cliente = %s")
        params.append(filtros["cliente"])
    if filtros.get("diretor_executivo"):
        filtros_gestores.append("cr.diretorexecutivo = %s")
        params.append(filtros["diretor_executivo"])
    if filtros.get("diretor_regional"):
        filtros_gestores.append("cr.diretorregional = %s")
        params.append(filtros["diretor_regional"])
    if filtros.get("gerente_regional"):
        filtros_gestores.append("cr.gerenteregional = %s")
        params.append(filtros["gerente_regional"])
    if filtros.get("gerente"):
        filtros_gestores.append("cr.gerente = %s")
        params.append(filtros["gerente"])
    if filtros.get("supervisor"):
        filtros_gestores.append("cr.supervisor = %s")
        params.append(filtros["supervisor"])
    if filtros.get("pec_01"):
        clauses.append("e.nivel_01 = %s")
        params.append(filtros["pec_01"])
    if filtros.get("pec_02"):
        clauses.append("e.nivel_02 = %s")
        params.append(filtros["pec_02"])

    if filtros_gestores:
        join_cr = "LEFT JOIN dw_vista.dm_cr cr ON e.id_cr = cr.id_cr"
        clauses.append("(" + " AND ".join(filtros_gestores) + ")")

    return " AND ".join(clauses), params, join_cr


def _finalizada_no_prazo(status: int, terminoreal, prazo, expirada: bool) -> bool:
    if status != 85:
        return False
    if expirada:
        return False
    if terminoreal is None:
        return True
    return terminoreal <= prazo


def _calc_pizza(stats_rows: List[tuple]) -> Dict[str, int]:
    finalizadas_no_prazo = 0
    total = 0
    for row in stats_rows:
        status, expirada, terminoreal, prazo, count = row
        total += count
        if _finalizada_no_prazo(status, terminoreal, prazo, expirada):
            finalizadas_no_prazo += count
    nao_realizadas = total - finalizadas_no_prazo
    return {"finalizadas": finalizadas_no_prazo, "nao_realizadas": nao_realizadas, "total": total}


def _fetch_dashboard_data(filtros: Dict[str, str]) -> Dict[str, Any]:
    conn = get_db_vista()
    cur = conn.cursor()

    agora = datetime.now(TIMEZONE_BRASILIA)
    seis_meses_atras = (agora.replace(day=1) - timedelta(days=1)).replace(day=1)

    # 1) Série diária do mês atual (total por dia)
    primeiro_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ultimo_mes = (primeiro_mes + timedelta(days=32)).replace(day=1) - timedelta(microseconds=1)
    where_mes, params_mes, join_mes = _where_and_params(filtros, primeiro_mes, ultimo_mes)
    cur.execute(
        f"""
        SELECT DATE(t.disponibilizacao) AS dia, COUNT(*) AS total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        {join_mes}
        WHERE {where_mes}
        GROUP BY DATE(t.disponibilizacao)
        ORDER BY dia
        """,
        params_mes,
    )
    diarios = [{"dia": row[0].isoformat(), "total": row[1]} for row in cur.fetchall()]

    # 2) Série mensal dos últimos 6 meses (inclusive mês atual)
    where_6m, params_6m, join_6m = _where_and_params(filtros, seis_meses_atras, ultimo_mes)
    cur.execute(
        f"""
        SELECT DATE_TRUNC('month', t.disponibilizacao) AS mes, COUNT(*) AS total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        {join_6m}
        WHERE {where_6m}
        GROUP BY mes
        ORDER BY mes
        """,
        params_6m,
    )
    mensais = [{"mes": row[0].date().isoformat(), "total": row[1]} for row in cur.fetchall()]

    # 3) Heatmap: CR x dia (porcentagem SLA)
    where_heat, params_heat, join_heat = _where_and_params(filtros, primeiro_mes, ultimo_mes)
    cur.execute(
        f"""
        SELECT 
            e.crno as cr,
            EXTRACT(DAY FROM t.disponibilizacao)::int as dia,
            SUM(CASE WHEN t.status = 85 AND t.expirada = FALSE AND (t.terminoreal IS NULL OR t.terminoreal <= t.prazo) THEN 1 ELSE 0 END) as finalizadas_prazo,
            COUNT(*) as total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        {join_heat}
        WHERE {where_heat}
        GROUP BY e.crno, EXTRACT(DAY FROM t.disponibilizacao)
        HAVING COUNT(*) > 0
        ORDER BY e.crno, dia
        """,
        params_heat,
    )
    heat_rows = cur.fetchall()
    heatmap = {}
    for cr, dia, finalizadas_prazo, total in heat_rows:
        porcent = (finalizadas_prazo / total * 100) if total else 0
        if cr not in heatmap:
            heatmap[cr] = {"cr": cr, "dias": {}}
        heatmap[cr]["dias"][dia] = round(porcent, 1)
    heatmap_list = list(heatmap.values())

    # 4) Pizza: finalizadas x não realizadas (considerando atraso como não realizada)
    where_pizza, params_pizza, join_pizza = _where_and_params(filtros, primeiro_mes, ultimo_mes)
    cur.execute(
        f"""
        SELECT 
            t.status,
            t.expirada,
            t.terminoreal,
            t.prazo,
            COUNT(*) as total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        {join_pizza}
        WHERE {where_pizza}
        GROUP BY t.status, t.expirada, t.terminoreal, t.prazo
        """,
        params_pizza,
    )
    pizza_rows = cur.fetchall()
    pizza_stats = _calc_pizza(pizza_rows)

    cur.close()
    conn.close()

    return {
        "serie_diaria": diarios,
        "serie_mensal": mensais,
        "heatmap": heatmap_list,
        "pizza": pizza_stats,
        "filtros": filtros,
        "periodo": {
            "inicio": primeiro_mes.isoformat(),
            "fim": ultimo_mes.isoformat(),
            "descricao": f"Mês {primeiro_mes.strftime('%m/%Y')}",
        },
    }


def atualizar_dashboard_cache(filtros: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """
    Gera os dados do dashboard e grava no Redis.
    """
    filtros_ok = _coerce_filters(filtros)
    logger.info(f"[Dashboard] Atualizando cache com filtros: {filtros_ok}")
    payload = _fetch_dashboard_data(filtros_ok)
    set_cached_dashboard(payload)
    return payload

