from app.models.database import get_db_vista


def buscar_tarefas_para_sla(cr_list, data_ini, data_fim, status_list):
    """
    Busca tarefas para SLA usando CR como chave primária
    Nome do contrato = nivel_03
    Local = concatenação de nivel_04/05/06/07
    """
    status_map = {
        'abertas': [10],
        'iniciadas': [25],
        'finalizadas': [85]
    }

    status_ids = []
    for nome in status_list:
        status_ids.extend(status_map.get(nome, []))

    # Verifica se deve incluir colunas extras para finalizadas
    incluir_finalizadas = 'finalizadas' in status_list

    conn = get_db_vista()
    cur = conn.cursor()
    cr_strings = [str(cr) for cr in cr_list]

    # Query com concatenação dos níveis para formar o Local
    if incluir_finalizadas:
        query = """
            SELECT
                E.crno AS "CR",
                E.nivel_03 AS "Contrato",
                CONCAT_WS('/', 
                    NULLIF(E.nivel_04, ''),
                    NULLIF(E.nivel_05, ''),
                    NULLIF(E.nivel_06, ''),
                    NULLIF(E.nivel_07, '')
                ) AS "Local",
                A.nome AS "Nome_Tarefa",
                A.disponibilizacao AS "Disponibilizacao",
                A.prazo::date AS "Prazo",
                A.inicioreal AS "Inicio_Real",
                A.terminoreal AS "Termino_Real",
                A.expirada AS "Expirada"
            FROM dbo.tarefa A
            INNER JOIN dw_vista.DM_ESTRUTURA E 
                ON E.Id_Estrutura = A.estruturaid
                AND E.crno = ANY(%s)
            WHERE A.disponibilizacao >= %s
              AND A.disponibilizacao < %s
              AND A.status = ANY(%s)
            ORDER BY E.crno, E.nivel_03, 
                CONCAT_WS('/', 
                    NULLIF(E.nivel_04, ''),
                    NULLIF(E.nivel_05, ''),
                    NULLIF(E.nivel_06, ''),
                    NULLIF(E.nivel_07, '')
                ), 
                A.disponibilizacao;
        """
    else:
        query = """
            SELECT
                E.crno AS "CR",
                E.nivel_03 AS "Contrato",
                CONCAT_WS('/', 
                    NULLIF(E.nivel_04, ''),
                    NULLIF(E.nivel_05, ''),
                    NULLIF(E.nivel_06, ''),
                    NULLIF(E.nivel_07, '')
                ) AS "Local",
                A.nome AS "Nome_Tarefa",
                A.disponibilizacao AS "Disponibilizacao",
                A.prazo::date AS "Prazo"
            FROM dbo.tarefa A
            INNER JOIN dw_vista.DM_ESTRUTURA E 
                ON E.Id_Estrutura = A.estruturaid
                AND E.crno = ANY(%s)
            WHERE A.disponibilizacao >= %s
              AND A.disponibilizacao < %s
              AND A.status = ANY(%s)
            ORDER BY E.crno, E.nivel_03, 
                CONCAT_WS('/', 
                    NULLIF(E.nivel_04, ''),
                    NULLIF(E.nivel_05, ''),
                    NULLIF(E.nivel_06, ''),
                    NULLIF(E.nivel_07, '')
                ), 
                A.disponibilizacao;
        """

    params = [cr_strings, data_ini, data_fim, status_ids]
    cur.execute(query, params)
    tarefas = cur.fetchall()
    conn.close()

    return tarefas, incluir_finalizadas


def buscar_nome_contrato_por_cr(cr):
    """
    Busca o nome do contrato (nivel_03) baseado no CR
    """
    conn = get_db_vista()
    cur = conn.cursor()

    query = """
        SELECT DISTINCT nivel_03 
        FROM dw_vista.DM_ESTRUTURA 
        WHERE crno = %s
        LIMIT 1
    """

    cur.execute(query, (str(cr),))
    resultado = cur.fetchone()
    conn.close()

    return resultado[0] if resultado else f"CR {cr}"
