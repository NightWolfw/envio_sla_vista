from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytz

from app.models.database import get_db_site
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


def _classificar(status: int, expirada: bool, terminoreal, prazo) -> str:
    """
    Retorna 'finalizada' se status=85, não expirada e (terminoreal <= prazo ou terminoreal é None),
    caso contrário 'nao_realizada'.
    """
    if status == 85 and not expirada:
        if terminoreal is None:
            return "finalizada"
        return "finalizada" if terminoreal <= prazo else "nao_realizada"
    return "nao_realizada"


def _fetch_dashboard_data(filtros: Dict[str, str]) -> Dict[str, Any]:
    conn = get_db_site()
    cur = conn.cursor()

    agora = datetime.now(TIMEZONE_BRASILIA)
    inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()
    fim_mes = (agora.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # Filtros preparados
    filtros_sql = []
    params: List[Any] = []
    if filtros.get("cr"):
        filtros_sql.append("cr = %s")
        params.append(filtros["cr"])
    if filtros.get("cliente"):
        filtros_sql.append("cliente = %s")
        params.append(filtros["cliente"])
    if filtros.get("diretor_executivo"):
        filtros_sql.append("diretor_executivo = %s")
        params.append(filtros["diretor_executivo"])
    if filtros.get("diretor_regional"):
        filtros_sql.append("diretor_regional = %s")
        params.append(filtros["diretor_regional"])
    if filtros.get("gerente_regional"):
        filtros_sql.append("gerente_regional = %s")
        params.append(filtros["gerente_regional"])
    if filtros.get("gerente"):
        filtros_sql.append("gerente = %s")
        params.append(filtros["gerente"])
    if filtros.get("supervisor"):
        filtros_sql.append("supervisor = %s")
        params.append(filtros["supervisor"])
    if filtros.get("pec_01"):
        filtros_sql.append("pec_01 = %s")
        params.append(filtros["pec_01"])
    if filtros.get("pec_02"):
        filtros_sql.append("pec_02 = %s")
        params.append(filtros["pec_02"])
    where_extra = (" AND " + " AND ".join(filtros_sql)) if filtros_sql else ""

    # Série diária (mês corrente) a partir do dw_sla
    cur.execute(
        f"""
        SELECT 
            data,
            SUM(finalizadas_ok) AS finalizadas,
            SUM(nao_realizadas) AS nao_realizadas
        FROM dashboard_tarefas_dia
        WHERE data >= %s AND data <= %s {where_extra}
        GROUP BY data
        ORDER BY data
        """,
        [inicio_mes, fim_mes] + params,
    )
    diarios = [
        {"dia": row[0].isoformat(), "finalizadas": row[1] or 0, "nao_realizadas": row[2] or 0}
        for row in cur.fetchall()
    ]

    # Heatmap (CR x dia)
    cur.execute(
        f"""
        SELECT 
            cr,
            data,
            SUM(finalizadas_ok) AS finalizadas,
            SUM(total) AS total
        FROM dashboard_tarefas_dia
        WHERE data >= %s AND data <= %s {where_extra}
        GROUP BY cr, data
        HAVING SUM(total) > 0
        ORDER BY cr, data
        """,
        [inicio_mes, fim_mes] + params,
    )
    heatmap = {}
    for cr, data, finalizadas, total in cur.fetchall():
        porcent = (finalizadas / total * 100) if total else 0
        dia = datetime.fromisoformat(str(data)).day
        if cr not in heatmap:
            heatmap[cr] = {"cr": cr, "dias": {}}
        heatmap[cr]["dias"][dia] = round(porcent, 1)
    heatmap_list = list(heatmap.values())

    # Pizza (finalizadas x não realizadas) no mês corrente
    cur.execute(
        f"""
        SELECT 
            SUM(finalizadas_ok) AS finalizadas,
            SUM(nao_realizadas) AS nao_realizadas,
            SUM(total) AS total
        FROM dashboard_tarefas_dia
        WHERE data >= %s AND data <= %s {where_extra}
        """,
        [inicio_mes, fim_mes] + params,
    )
    row_pizza = cur.fetchone() or (0, 0, 0)
    pizza_stats = {
        "finalizadas": row_pizza[0] or 0,
        "nao_realizadas": row_pizza[1] or 0,
        "total": row_pizza[2] or 0,
    }

    # Ranking de executores (top 20)
    cur.execute(
        f"""
        SELECT 
            executor,
            SUM(finalizadas_ok) AS finalizadas,
            SUM(nao_realizadas) AS nao_realizadas,
            SUM(total) AS total
        FROM dashboard_executores
        WHERE atualizado_em >= %s AND atualizado_em <= %s {where_extra}
        GROUP BY executor
        HAVING SUM(total) > 0
        ORDER BY finalizadas DESC, total DESC
        LIMIT 20
        """,
        [inicio_mes, fim_mes] + params,
    )
    ranking = [
        {
            "executor": r[0],
            "finalizadas": r[1] or 0,
            "nao_realizadas": r[2] or 0,
            "total": r[3] or 0,
        }
        for r in cur.fetchall()
    ]

    cur.close()
    conn.close()

    payload = {
        "serie_diaria": diarios,
        "serie_mensal": [],  # removido conforme solicitação
        "heatmap": heatmap_list,
        "pizza": pizza_stats,
        "ranking_executores": ranking,
        "filtros": filtros,
        "periodo": {
            "inicio": inicio_mes.isoformat(),
            "fim": fim_mes.isoformat(),
            "descricao": f"Mês {inicio_mes.strftime('%m/%Y')}",
        },
    }
    return payload


def atualizar_dashboard_cache(filtros: Dict[str, Optional[str]], etl_attempts: Optional[int] = None) -> Dict[str, Any]:
    """
    Gera os dados do dashboard e grava no Redis.
    """
    filtros_ok = _coerce_filters(filtros)
    logger.info(f"[Dashboard] Atualizando cache com filtros: {filtros_ok}")
    payload = _fetch_dashboard_data(filtros_ok)
    if etl_attempts is not None:
        payload["etl_attempts"] = etl_attempts
    set_cached_dashboard(payload, filtros_ok)
    return payload
