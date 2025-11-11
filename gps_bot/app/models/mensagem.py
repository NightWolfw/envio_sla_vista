from app.models.database import get_db_site


def listar_mensagens(apenas_ativas=None):
    """Lista mensagens agendadas"""
    conn = get_db_site()
    cur = conn.cursor()

    query = "SELECT * FROM mensagens_agendadas WHERE 1=1"
    params = []

    if apenas_ativas is not None:
        query += " AND ativo = %s"
        params.append(apenas_ativas)

    query += " ORDER BY criado_em DESC"

    cur.execute(query, params)
    mensagens = cur.fetchall()
    cur.close()
    conn.close()

    return mensagens


def obter_mensagem(mensagem_id):
    """Busca mensagem específica"""
    conn = get_db_site()
    cur = conn.cursor()

    cur.execute("SELECT * FROM mensagens_agendadas WHERE id = %s", (mensagem_id,))
    mensagem = cur.fetchone()

    cur.close()
    conn.close()
    return mensagem


def criar_mensagem(dados):
    """Cria nova mensagem agendada"""
    conn = get_db_site()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO mensagens_agendadas 
        (mensagem, grupos_selecionados, tipo_recorrencia, dias_semana, 
         horario, data_inicio, data_fim)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (dados['mensagem'], dados['grupos_ids'], dados['tipo_recorrencia'],
          dados['dias_semana'], dados['horario'], dados['data_inicio'],
          dados['data_fim']))

    mensagem_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return mensagem_id


def atualizar_mensagem(mensagem_id, dados):
    """Atualiza mensagem existente"""
    conn = get_db_site()
    cur = conn.cursor()

    cur.execute("""
        UPDATE mensagens_agendadas 
        SET mensagem = %s, grupos_selecionados = %s, 
            tipo_recorrencia = %s, dias_semana = %s, 
            horario = %s, data_inicio = %s, data_fim = %s,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (dados['mensagem'], dados['grupos_ids'], dados['tipo_recorrencia'],
          dados['dias_semana'], dados['horario'], dados['data_inicio'],
          dados['data_fim'], mensagem_id))

    conn.commit()
    cur.close()
    conn.close()


def deletar_mensagem(mensagem_id):
    """Deleta mensagem"""
    conn = get_db_site()
    cur = conn.cursor()

    cur.execute("DELETE FROM mensagens_agendadas WHERE id = %s", (mensagem_id,))

    conn.commit()
    cur.close()
    conn.close()


def toggle_ativa(mensagem_id):
    """Ativa/desativa mensagem"""
    conn = get_db_site()
    cur = conn.cursor()

    cur.execute("SELECT ativo FROM mensagens_agendadas WHERE id = %s", (mensagem_id,))
    ativo_atual = cur.fetchone()[0]
    novo_status = not ativo_atual

    cur.execute("UPDATE mensagens_agendadas SET ativo = %s WHERE id = %s",
                (novo_status, mensagem_id))

    conn.commit()
    cur.close()
    conn.close()

    return novo_status
