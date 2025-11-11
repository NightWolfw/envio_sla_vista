from app.models.database import get_db_vista

def buscar_tarefas_para_sla(cr_list, data_ini, data_fim, status_list):
    status_map = {
        'abertas': [10],
        'iniciadas': [25],
        'finalizadas': [85]
    }
    status_ids = []
    for nome in status_list:
        status_ids.extend(status_map.get(nome, []))

    conn = get_db_vista()
    cur = conn.cursor()
    cr_strings = [str(cr) for cr in cr_list]

    query = """
        SELECT
            E.nomecontrato AS "Contrato",
            E.nome AS "Local",
            A.nome AS "Nome_Tarefa",
            A.disponibilizacao AS "Disponibilizacao",
            A.prazo::date AS "Prazo"
        FROM dbo.tarefa A
        INNER JOIN dw_vista.DM_ESTRUTURA E ON E.Id_Estrutura = A.estruturaid
            AND E.crno = ANY(%s)
        WHERE A.disponibilizacao >= %s
          AND A.disponibilizacao < %s
          AND A.status = ANY(%s)
        ORDER BY E.nomecontrato, E.nome, A.disponibilizacao;
    """

    params = [cr_strings, data_ini, data_fim, status_ids]
    cur.execute(query, params)
    tarefas = cur.fetchall()
    conn.close()
    return tarefas
