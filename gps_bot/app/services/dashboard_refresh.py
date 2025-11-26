from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytz

from app.models.database import conectar_com_retry
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
    tentativas = 0
    delay = 3.0
    conn = None
    while conn is None:
        tentativas += 1
        try:
            conn = conectar_com_retry(
                DB_CONFIG,
                max_tentativas=1,
                delay_inicial=int(delay),
                db_nome="Vista-dashboard",
            )
        except Exception as exc:
            logger.warning(f"[Dashboard] Tentativa {tentativas} falhou: {exc}")
            time.sleep(delay)
            continue

    cur = conn.cursor()

    agora = datetime.now(TIMEZONE_BRASILIA)
    inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fim_agora = agora  # até a data/hora atual

    where_sql, params_base, join_cr = _where_and_params(filtros, inicio_mes, fim_agora)

    # Série diária (mês corrente até agora)
    cur.execute(
        f"""
        SELECT 
            DATE(t.disponibilizacao) AS dia,
            t.status,
            t.expirada,
            t.terminoreal,
            t.prazo,
            COUNT(*) AS total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        {join_cr}
        WHERE {where_sql}
        GROUP BY DATE(t.disponibilizacao), t.status, t.expirada, t.terminoreal, t.prazo
        ORDER BY DATE(t.disponibilizacao)
        """,
        params_base,
    )
    diarios_tmp = {}
    for row in cur.fetchall():
        dia = row[0].isoformat()
        status, expirada, terminoreal, prazo, total = row[1], row[2], row[3], row[4], row[5]
        cls = _classificar(status, expirada, terminoreal, prazo)
        if dia not in diarios_tmp:
            diarios_tmp[dia] = {"dia": dia, "finalizadas": 0, "nao_realizadas": 0}
        diarios_tmp[dia][cls == "finalizada" and "finalizadas" or "nao_realizadas"] += total
    diarios = sorted(diarios_tmp.values(), key=lambda x: x["dia"])

    # Heatmap (CR x dia)
    cur.execute(
        f"""
        SELECT 
            e.crno as cr,
            EXTRACT(DAY FROM t.disponibilizacao)::int as dia,
            SUM(CASE WHEN t.status = 85 AND t.expirada = FALSE AND (t.terminoreal IS NULL OR t.terminoreal <= t.prazo) THEN 1 ELSE 0 END) as finalizadas_prazo,
            COUNT(*) as total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        {join_cr}
        WHERE {where_sql}
        GROUP BY e.crno, EXTRACT(DAY FROM t.disponibilizacao)
        HAVING COUNT(*) > 0
        ORDER BY e.crno, dia
        """,
        params_base,
    )
    heatmap = {}
    for cr, dia, finalizadas_prazo, total in cur.fetchall():
        porcent = (finalizadas_prazo / total * 100) if total else 0
        if cr not in heatmap:
            heatmap[cr] = {"cr": cr, "dias": {}}
        heatmap[cr]["dias"][dia] = round(porcent, 1)
    heatmap_list = list(heatmap.values())

    # Pizza (finalizadas x não realizadas) no mês corrente
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
        {join_cr}
        WHERE {where_sql}
        GROUP BY t.status, t.expirada, t.terminoreal, t.prazo
        """,
        params_base,
    )
    pizza_rows = cur.fetchall()
    pizza_stats = _calc_pizza(pizza_rows)

    # Ranking executores (top 20)
    cur.execute(
        f"""
        SELECT 
            COALESCE(r.nome, 'Sem Executor') as executor,
            SUM(CASE WHEN t.status = 85 AND t.expirada = FALSE AND (t.terminoreal IS NULL OR t.terminoreal <= t.prazo) THEN 1 ELSE 0 END) AS finalizadas_ok,
            SUM(CASE WHEN t.status = 85 AND ((t.expirada = TRUE) OR (t.expirada = FALSE AND t.terminoreal IS NOT NULL AND t.terminoreal > t.prazo)) THEN 1 ELSE 0 END) AS nao_realizadas,
            COUNT(*) AS total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        LEFT JOIN dbo.recurso r ON t.finalizadoporhash = r.codigohash
        {join_cr}
        WHERE {where_sql}
        GROUP BY executor
        HAVING COUNT(*) > 0
        ORDER BY total DESC
        LIMIT 20
        """,
        params_base,
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
        "serie_mensal": [],
        "heatmap": heatmap_list,
        "pizza": pizza_stats,
        "ranking_executores": ranking,
        "etl_attempts": tentativas,
        "filtros": filtros,
        "periodo": {
            "inicio": inicio_mes.isoformat(),
            "fim": fim_agora.isoformat(),
            "descricao": f"Mês {inicio_mes.strftime('%m/%Y')} até {fim_agora.strftime('%d/%m %H:%M')}",
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
