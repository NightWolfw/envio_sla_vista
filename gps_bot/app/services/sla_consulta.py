"""
Service para consultar tarefas do GPS Vista
"""
import logging
from datetime import datetime

from app.models.database import get_db_vista

logger = logging.getLogger(__name__)


def buscar_tarefas_por_periodo(cr, data_inicio, data_fim, tipo_envio='resultados', return_meta: bool = False):
    """
    Busca tarefas no Vista por CR e período de disponibilização

    Args:
        cr: Centro de Resultado
        data_inicio: datetime início do período
        data_fim: datetime fim do período
        tipo_envio: 'resultados' ou 'programadas'

    Returns:
        dict com contadores por status
    """
    conn = get_db_vista()
    cur = conn.cursor()

    # Query com JOINs corretos e expirada como boolean
    query = """
        SELECT 
            t.status,
            t.expirada,
            COUNT(*) as total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        WHERE e.crno = %s
          AND t.disponibilizacao >= %s
          AND t.disponibilizacao <= %s
          AND t.status IN (10, 25, 85)
        GROUP BY t.status, t.expirada
    """

    params = (cr, data_inicio, data_fim)
    cur.execute(query, params)
    resultados = cur.fetchall()

    logger.info(
        "[SLA] Consulta agregada tarefas CR=%s tipo=%s inicio=%s fim=%s rows=%s",
        cr,
        tipo_envio,
        data_inicio,
        data_fim,
        len(resultados),
    )

    # Inicializa contadores
    stats = {
        'finalizadas': 0,
        'nao_realizadas': 0,
        'em_aberto': 0,
        'iniciadas': 0
    }

    # Preenche com resultados (expirada é boolean)
    for row in resultados:
        status = row[0]
        expirada = row[1]  # True ou False
        total = row[2]

        if status == 85 and expirada == False:
            stats['finalizadas'] = total
        elif status == 85 and expirada == True:
            stats['nao_realizadas'] = total
        elif status == 10:
            stats['em_aberto'] = total
        elif status == 25:
            stats['iniciadas'] = total

    cur.close()
    conn.close()

    if return_meta:
        meta = {
            "query": query.strip(),
            "params": {
                "cr": cr,
                "data_inicio": data_inicio.isoformat(),
                "data_fim": data_fim.isoformat(),
                "tipo_envio": tipo_envio,
            },
            "rows": len(resultados),
        }
        return stats, meta

    return stats


def buscar_tarefas_detalhadas(cr, data_inicio, data_fim, tipos_status=None, return_meta: bool = False):
    """
    Busca detalhes das tarefas para geração de PDF
    """
    conn = get_db_vista()
    cur = conn.cursor()

    # Monta condições
    condicoes = []

    if not tipos_status:
        tipos_status = ['finalizadas', 'nao_realizadas', 'em_aberto', 'iniciadas']

    if 'finalizadas' in tipos_status:
        condicoes.append("(t.status = 85 AND t.expirada = FALSE)")

    if 'nao_realizadas' in tipos_status:
        condicoes.append("(t.status = 85 AND t.expirada = TRUE)")

    if 'em_aberto' in tipos_status:
        condicoes.append("(t.status = 10)")

    if 'iniciadas' in tipos_status:
        condicoes.append("(t.status = 25)")

    where_status = " OR ".join(condicoes) if condicoes else "1=0"

    # ✅ MUDANÇA: t.nome em vez de t.descricao
    query = f"""
        SELECT 
            t.numero,
            t.nome AS descricao,
            t.disponibilizacao,
            t.prazo,
            t.inicioreal,
            t.terminoreal,
            t.status,
            t.expirada,
            COALESCE(rf.nome, ri.nome) AS executor,
            COALESCE(
                NULLIF(CONCAT_WS('/', 
                    NULLIF(e.nivel_05, ''), 
                    NULLIF(e.nivel_06, ''), 
                    NULLIF(e.nivel_07, '')
                ), ''),
                'N/A'
            ) AS local,
            CASE 
                WHEN t.status = 85 AND t.expirada = FALSE THEN 'Finalizada'
                WHEN t.status = 85 AND t.expirada = TRUE THEN 'Não Realizada'
                WHEN t.status = 10 THEN 'Em Aberto'
                WHEN t.status = 25 THEN 'Iniciada'
            END AS status_texto
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        LEFT JOIN dbo.recurso rf ON t.finalizadoporhash = rf.codigohash
        LEFT JOIN dbo.recurso ri ON t.iniciadoporhash = ri.codigohash
        WHERE e.crno = %s
          AND t.disponibilizacao >= %s
          AND t.disponibilizacao <= %s
          AND ({where_status})
        ORDER BY t.disponibilizacao, status_texto
    """

    params = (cr, data_inicio, data_fim)
    cur.execute(query, params)

    colunas = [desc[0] for desc in cur.description]
    tarefas = []

    for row in cur.fetchall():
        tarefa = dict(zip(colunas, row))
        tarefas.append(tarefa)

    sample_numeros = [t.get('numero') for t in tarefas[:3] if t.get('numero') is not None]
    logger.info(
        "[SLA] Consulta detalhada tarefas CR=%s inicio=%s fim=%s filtros=%s rows=%s sample_numeros=%s",
        cr,
        data_inicio,
        data_fim,
        tipos_status,
        len(tarefas),
        sample_numeros,
    )

    cur.close()
    conn.close()

    if return_meta:
        meta = {
            "query": query.strip(),
            "params": {
                "cr": cr,
                "data_inicio": data_inicio.isoformat(),
                "data_fim": data_fim.isoformat(),
                "tipos_status": tipos_status,
            },
            "rows": len(tarefas),
            "sample_numeros": sample_numeros,
        }
        return tarefas, meta

    return tarefas
