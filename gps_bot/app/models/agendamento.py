"""
Model para agendamento de envio de SLA
"""
from app.models.database import get_db_site
from datetime import datetime


def criar_agendamento(dados):
    """Cria novo agendamento de SLA"""
    conn = get_db_site()
    cur = conn.cursor()

    query = """
        INSERT INTO agendamentos_sla 
        (grupo_id, tipo_envio, dias_semana, data_envio, 
         hora_inicio, dia_offset_inicio, hora_fim, dia_offset_fim, criado_em)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """

    cur.execute(query, (
        dados['grupo_id'],
        dados['tipo_envio'],
        dados['dias_semana'],  # CSV: 'seg,ter,qua'
        dados['data_envio'],
        dados['hora_inicio'],
        dados['dia_offset_inicio'],
        dados['hora_fim'],
        dados['dia_offset_fim'],
        datetime.now()
    ))

    agendamento_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return agendamento_id


def listar_agendamentos(grupo_id=None):
    """Lista agendamento, opcionalmente filtrado por grupo"""
    conn = get_db_site()
    cur = conn.cursor()

    query = """
        SELECT a.id, a.grupo_id, g.nome_grupo, g.cr, 
               a.tipo_envio, a.dias_semana, a.data_envio,
               a.hora_inicio, a.dia_offset_inicio, 
               a.hora_fim, a.dia_offset_fim, a.criado_em
        FROM agendamentos_sla a
        JOIN grupos_whatsapp g ON a.grupo_id = g.id
        WHERE 1=1
    """
    params = []

    if grupo_id:
        query += " AND a.grupo_id = %s"
        params.append(grupo_id)

    query += " ORDER BY a.data_envio DESC"

    cur.execute(query, params)
    agendamentos = cur.fetchall()
    cur.close()
    conn.close()

    return agendamentos


def obter_agendamento(agendamento_id):
    """Busca agendamento específico por ID"""
    conn = get_db_site()
    cur = conn.cursor()

    query = """
        SELECT a.*, g.nome_grupo, g.cr, g.group_id
        FROM agendamentos_sla a
        JOIN grupos_whatsapp g ON a.grupo_id = g.id
        WHERE a.id = %s
    """

    cur.execute(query, (agendamento_id,))
    agendamento = cur.fetchone()
    cur.close()
    conn.close()

    return agendamento


def deletar_agendamento(agendamento_id):
    """Remove agendamento"""
    conn = get_db_site()
    cur = conn.cursor()

    cur.execute("DELETE FROM agendamentos_sla WHERE id = %s", (agendamento_id,))

    conn.commit()
    cur.close()
    conn.close()


def atualizar_agendamento(agendamento_id, dados):
    """Atualiza dados do agendamento"""
    conn = get_db_site()
    cur = conn.cursor()

    query = """
        UPDATE agendamentos_sla 
        SET tipo_envio = %s, dias_semana = %s, data_envio = %s,
            hora_inicio = %s, dia_offset_inicio = %s,
            hora_fim = %s, dia_offset_fim = %s
        WHERE id = %s
    """

    cur.execute(query, (
        dados['tipo_envio'],
        dados['dias_semana'],
        dados['data_envio'],
        dados['hora_inicio'],
        dados['dia_offset_inicio'],
        dados['hora_fim'],
        dados['dia_offset_fim'],
        agendamento_id
    ))

    conn.commit()
    cur.close()
    conn.close()
