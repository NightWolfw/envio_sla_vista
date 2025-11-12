"""
Service para consultar tarefas do GPS Vista
"""
from app.models.database import get_db_vista
from datetime import datetime


def buscar_tarefas_por_periodo(cr, data_inicio, data_fim, tipo_envio='resultados'):
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

    cur.execute(query, (cr, data_inicio, data_fim))
    resultados = cur.fetchall()

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

    return stats


def buscar_tarefas_detalhadas(cr, data_inicio, data_fim, tipos_status=None):
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

    # Query COM LOCAL (COALESCE para valores nulos) e inicioreal/terminoreal
    query = f"""
        SELECT 
            t.numero,
            t.descricao,
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

    cur.execute(query, (cr, data_inicio, data_fim))

    colunas = [desc[0] for desc in cur.description]
    tarefas = []

    for row in cur.fetchall():
        tarefa = dict(zip(colunas, row))
        tarefas.append(tarefa)

    cur.close()
    conn.close()

    return tarefas

