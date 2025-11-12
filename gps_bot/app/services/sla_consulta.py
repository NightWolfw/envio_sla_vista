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

    # Query base
    query = """
        SELECT 
            id_status,
            CASE 
                WHEN id_status = 85 AND expirada = 0 THEN 'finalizadas'
                WHEN id_status = 85 AND expirada = 1 THEN 'nao_realizadas'
                WHEN id_status = 10 THEN 'em_aberto'
                WHEN id_status = 25 THEN 'iniciadas'
            END AS categoria,
            COUNT(*) as total
        FROM dbo.tarefa
        WHERE cr = %s
          AND disponibilizacao >= %s
          AND disponibilizacao <= %s
          AND id_status IN (10, 25, 85)
        GROUP BY id_status, expirada
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

    # Preenche com resultados
    for row in resultados:
        categoria = row[1]
        total = row[2]
        if categoria:
            stats[categoria] = total

    cur.close()
    conn.close()

    return stats


def buscar_tarefas_detalhadas(cr, data_inicio, data_fim, tipos_status=None):
    """
    Busca detalhes das tarefas para geração de PDF

    Args:
        cr: Centro de Resultado
        data_inicio: datetime início
        data_fim: datetime fim
        tipos_status: lista de tipos ['finalizadas', 'nao_realizadas', 'em_aberto', 'iniciadas']

    Returns:
        Lista de dicts com dados das tarefas
    """
    conn = get_db_vista()
    cur = conn.cursor()

    # Monta condições baseado nos tipos solicitados
    condicoes = []

    if not tipos_status:
        tipos_status = ['finalizadas', 'nao_realizadas', 'em_aberto', 'iniciadas']

    if 'finalizadas' in tipos_status:
        condicoes.append("(t.id_status = 85 AND t.expirada = 0)")

    if 'nao_realizadas' in tipos_status:
        condicoes.append("(t.id_status = 85 AND t.expirada = 1)")

    if 'em_aberto' in tipos_status:
        condicoes.append("(t.id_status = 10)")

    if 'iniciadas' in tipos_status:
        condicoes.append("(t.id_status = 25)")

    where_status = " OR ".join(condicoes) if condicoes else "1=0"

    # Query COM JOIN para pegar executor
    query = f"""
        SELECT 
            t.id_tarefa,
            t.descricao,
            t.disponibilizacao,
            t.id_status,
            t.expirada,
            COALESCE(rf.nome, ri.nome) AS executor,
            CASE 
                WHEN t.id_status = 85 AND t.expirada = 0 THEN 'Finalizada'
                WHEN t.id_status = 85 AND t.expirada = 1 THEN 'Não Realizada'
                WHEN t.id_status = 10 THEN 'Em Aberto'
                WHEN t.id_status = 25 THEN 'Iniciada'
            END AS status_texto
        FROM dbo.tarefa t
        LEFT JOIN dbo.recurso rf ON t.finalizadoporhash = rf.codigohash
        LEFT JOIN dbo.recurso ri ON t.iniciadoporhash = ri.codigohash
        WHERE t.cr = %s
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
