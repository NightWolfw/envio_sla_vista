from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

import pytz

from app.models.database import conectar_com_retry, get_db_site
from config import DB_CONFIG

logger = logging.getLogger(__name__)
TIMEZONE_BRASILIA = pytz.timezone("America/Sao_Paulo")


def _intervalo_mes_atual():
    agora = datetime.now(TIMEZONE_BRASILIA)
    inicio = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fim = (inicio + timedelta(days=32)).replace(day=1) - timedelta(microseconds=1)
    return inicio, fim


def _coerce_filters(filtros: Dict[str, Optional[str]]) -> Dict[str, str]:
    base = {k: v for k, v in filtros.items() if v}
    if "diretor_executivo" not in base:
        base["diretor_executivo"] = "MARCOS NASCIMENTO PEDREIRA"
    return base


def _conectar_vista_sem_limite() -> tuple:
    """
    Tenta conectar ao Vista repetidamente até conseguir, registrando número de tentativas.
    """
    tentativas = 0
    delay = 2.0
    while True:
        tentativas += 1
        try:
            conn = conectar_com_retry(
                DB_CONFIG,
                max_tentativas=1,  # uma tentativa por ciclo
                delay_inicial=int(delay),
                db_nome="Vista-dashboard",
            )
            return conn, tentativas
        except Exception as exc:
            logger.warning(f"[Vista-dashboard] Tentativa {tentativas} falhou: {exc}")
            delay = min(delay * 1.5, 30)
            logger.warning(f"[Vista-dashboard] Reagendando nova tentativa em {delay:.1f}s...")
            time.sleep(delay)


def carregar_mes_corrente(filtros: Dict[str, Optional[str]] | None = None) -> int:
    """
    ETL: lê do Vista (dw_gps) o mês corrente e grava agregados no dw_sla (dashboard_tarefas_dia e dashboard_executores).
    Remove dados anteriores do mês antes de inserir.
    """
    filtros_ok = _coerce_filters(filtros or {})
    inicio, fim = _intervalo_mes_atual()

    # Conexão Vista (tenta até conseguir)
    conn_vista, tentativas = _conectar_vista_sem_limite()
    cur_v = conn_vista.cursor()

    # Conexão dw_sla
    conn_sla = get_db_site()
    cur_s = conn_sla.cursor()

    # Limpa dados do mês corrente
    cur_s.execute("DELETE FROM dashboard_tarefas_dia WHERE data >= %s AND data <= %s", (inicio.date(), fim.date()))
    cur_s.execute("DELETE FROM dashboard_executores WHERE atualizado_em >= %s AND atualizado_em <= %s", (inicio, fim))

    where = ["t.disponibilizacao >= %s", "t.disponibilizacao <= %s"]
    params = [inicio, fim]
    join_cr = ""
    filtros_gestores = []

    if filtros_ok.get("cr"):
        where.append("e.crno = %s")
        params.append(filtros_ok["cr"])
    if filtros_ok.get("cliente"):
        where.append("e.cliente = %s")
        params.append(filtros_ok["cliente"])
    if filtros_ok.get("diretor_executivo"):
        filtros_gestores.append("cr.diretorexecutivo = %s")
        params.append(filtros_ok["diretor_executivo"])
    if filtros_ok.get("diretor_regional"):
        filtros_gestores.append("cr.diretorregional = %s")
        params.append(filtros_ok["diretor_regional"])
    if filtros_ok.get("gerente_regional"):
        filtros_gestores.append("cr.gerenteregional = %s")
        params.append(filtros_ok["gerente_regional"])
    if filtros_ok.get("gerente"):
        filtros_gestores.append("cr.gerente = %s")
        params.append(filtros_ok["gerente"])
    if filtros_ok.get("supervisor"):
        filtros_gestores.append("cr.supervisor = %s")
        params.append(filtros_ok["supervisor"])
    if filtros_ok.get("pec_01"):
        where.append("e.nivel_01 = %s")
        params.append(filtros_ok["pec_01"])
    if filtros_ok.get("pec_02"):
        where.append("e.nivel_02 = %s")
        params.append(filtros_ok["pec_02"])
    if filtros_gestores:
        join_cr = "LEFT JOIN dw_vista.dm_cr cr ON e.id_cr = cr.id_cr"
        where.append("(" + " AND ".join(filtros_gestores) + ")")

    where_sql = " AND ".join(where)

    # 1) Agregação diária
    cur_v.execute(
        f"""
        SELECT 
            DATE(t.disponibilizacao) AS dia,
            e.crno,
            e.cliente,
            cr.diretorexecutivo,
            cr.diretorregional,
            cr.gerenteregional,
            cr.gerente,
            cr.supervisor,
            e.nivel_01,
            e.nivel_02,
            SUM(CASE WHEN t.status = 85 AND t.expirada = FALSE AND (t.terminoreal IS NULL OR t.terminoreal <= t.prazo) THEN 1 ELSE 0 END) AS finalizadas_ok,
            SUM(CASE WHEN t.status = 85 AND ((t.expirada = TRUE) OR (t.expirada = FALSE AND t.terminoreal IS NOT NULL AND t.terminoreal > t.prazo)) THEN 1 ELSE 0 END) AS nao_realizadas,
            SUM(CASE WHEN t.status = 10 THEN 1 ELSE 0 END) AS em_aberto,
            SUM(CASE WHEN t.status = 25 THEN 1 ELSE 0 END) AS iniciadas,
            COUNT(*) AS total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        {join_cr}
        WHERE {where_sql}
        GROUP BY DATE(t.disponibilizacao), e.crno, e.cliente, cr.diretorexecutivo, cr.diretorregional, cr.gerenteregional, cr.gerente, cr.supervisor, e.nivel_01, e.nivel_02
        HAVING COUNT(*) > 0
        ORDER BY dia
        """,
        params,
    )
    rows_dia = cur_v.fetchall()
    cur_s.executemany(
        """
        INSERT INTO dashboard_tarefas_dia (
            data, cr, cliente, diretor_executivo, diretor_regional, gerente_regional, gerente, supervisor, pec_01, pec_02,
            finalizadas_ok, nao_realizadas, em_aberto, iniciadas, total, atualizado_em
        ) VALUES (
            %(data)s, %(cr)s, %(cliente)s, %(diretor_executivo)s, %(diretor_regional)s, %(gerente_regional)s, %(gerente)s, %(supervisor)s, %(pec_01)s, %(pec_02)s,
            %(finalizadas_ok)s, %(nao_realizadas)s, %(em_aberto)s, %(iniciadas)s, %(total)s, NOW()
        )
        """,
        [
            {
                "data": r[0],
                "cr": r[1],
                "cliente": r[2],
                "diretor_executivo": r[3],
                "diretor_regional": r[4],
                "gerente_regional": r[5],
                "gerente": r[6],
                "supervisor": r[7],
                "pec_01": r[8],
                "pec_02": r[9],
                "finalizadas_ok": r[10],
                "nao_realizadas": r[11],
                "em_aberto": r[12],
                "iniciadas": r[13],
                "total": r[14],
            }
            for r in rows_dia
        ],
    )

    # 2) Ranking executores (mês corrente)
    cur_v.execute(
        f"""
        SELECT 
            COALESCE(r.nome, 'Sem Executor') as executor,
            e.crno,
            e.cliente,
            cr.diretorexecutivo,
            cr.diretorregional,
            cr.gerenteregional,
            cr.gerente,
            cr.supervisor,
            e.nivel_01,
            e.nivel_02,
            SUM(CASE WHEN t.status = 85 AND t.expirada = FALSE AND (t.terminoreal IS NULL OR t.terminoreal <= t.prazo) THEN 1 ELSE 0 END) AS finalizadas_ok,
            SUM(CASE WHEN t.status = 85 AND ((t.expirada = TRUE) OR (t.expirada = FALSE AND t.terminoreal IS NOT NULL AND t.terminoreal > t.prazo)) THEN 1 ELSE 0 END) AS nao_realizadas,
            COUNT(*) AS total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        LEFT JOIN dbo.recurso r ON t.finalizadoporhash = r.codigohash
        {join_cr}
        WHERE {where_sql}
        GROUP BY executor, e.crno, e.cliente, cr.diretorexecutivo, cr.diretorregional, cr.gerenteregional, cr.gerente, cr.supervisor, e.nivel_01, e.nivel_02
        HAVING COUNT(*) > 0
        ORDER BY total DESC
        """,
        params,
    )
    rows_exec = cur_v.fetchall()
    cur_s.executemany(
        """
        INSERT INTO dashboard_executores (
            executor, cr, cliente, diretor_executivo, diretor_regional, gerente_regional, gerente, supervisor, pec_01, pec_02,
            finalizadas_ok, nao_realizadas, total, atualizado_em
        ) VALUES (
            %(executor)s, %(cr)s, %(cliente)s, %(diretor_executivo)s, %(diretor_regional)s, %(gerente_regional)s, %(gerente)s, %(supervisor)s, %(pec_01)s, %(pec_02)s,
            %(finalizadas_ok)s, %(nao_realizadas)s, %(total)s, NOW()
        )
        """,
        [
            {
                "executor": r[0],
                "cr": r[1],
                "cliente": r[2],
                "diretor_executivo": r[3],
                "diretor_regional": r[4],
                "gerente_regional": r[5],
                "gerente": r[6],
                "supervisor": r[7],
                "pec_01": r[8],
                "pec_02": r[9],
                "finalizadas_ok": r[10],
                "nao_realizadas": r[11],
                "total": r[12],
            }
            for r in rows_exec
        ],
    )

    conn_sla.commit()
    cur_v.close()
    conn_vista.close()
    cur_s.close()
    conn_sla.close()
    logger.info(f"[Dashboard ETL] Atualizado mês corrente {inicio.date()} -> {fim.date()} com {len(rows_dia)} dias e {len(rows_exec)} executores. Tentativas de conexão: {tentativas}.")

    return tentativas
