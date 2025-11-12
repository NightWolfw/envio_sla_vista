from app.models.database import get_db_site
from datetime import datetime
import pytz

# Timezone de Brasília
TIMEZONE_BRASILIA = pytz.timezone('America/Sao_Paulo')


def criar_agendamento(dados):
    """Cria novo agendamento"""
    conn = get_db_site()
    cur = conn.cursor()

    query = """
        INSERT INTO agendamentos 
        (grupo_id, tipo_envio, dias_semana, data_envio, hora_inicio, 
         dia_offset_inicio, hora_fim, dia_offset_fim, ativo, criado_em)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, NOW())
        RETURNING id
    """

    cur.execute(query, (
        dados['grupo_id'],
        dados['tipo_envio'],
        dados['dias_semana'],
        dados['data_envio'],
        dados['hora_inicio'],
        dados['dia_offset_inicio'],
        dados['hora_fim'],
        dados['dia_offset_fim']
    ))

    agendamento_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return agendamento_id


def listar_agendamentos():
    """Lista todos os agendamentos com informações dos grupos"""
    conn = get_db_site()
    cur = conn.cursor()

    query = """
        SELECT 
            a.id,
            a.grupo_id,
            g.nome_grupo,
            g.cr,
            a.tipo_envio,
            a.dias_semana,
            a.data_envio,
            a.hora_inicio,
            a.dia_offset_inicio,
            a.hora_fim,
            a.dia_offset_fim,
            a.ativo,
            a.criado_em
        FROM agendamentos a
        INNER JOIN grupos_whatsapp g ON a.grupo_id = g.id
        ORDER BY a.criado_em DESC
    """

    cur.execute(query)
    rows = cur.fetchall()

    agendamentos = []
    for row in rows:
        # Converte para timezone de Brasília
        data_envio = row[6]
        if data_envio.tzinfo is None:
            data_envio = TIMEZONE_BRASILIA.localize(data_envio)
        else:
            data_envio = data_envio.astimezone(TIMEZONE_BRASILIA)

        agendamentos.append({
            'id': row[0],
            'grupo_id': row[1],
            'nome_grupo': row[2],
            'cr': row[3],
            'tipo_envio': row[4],
            'dias_semana': row[5],
            'data_envio': data_envio,
            'proximo_envio': data_envio.strftime('%d/%m/%Y %H:%M'),
            'hora_inicio': row[7],
            'dia_offset_inicio': row[8],
            'hora_fim': row[9],
            'dia_offset_fim': row[10],
            'ativo': row[11],
            'criado_em': row[12]
        })

    cur.close()
    conn.close()

    return agendamentos


def obter_agendamento(agendamento_id):
    """Busca agendamento específico"""
    conn = get_db_site()
    cur = conn.cursor()

    query = """
        SELECT * FROM agendamentos WHERE id = %s
    """

    cur.execute(query, (agendamento_id,))
    agendamento = cur.fetchone()

    cur.close()
    conn.close()

    return agendamento


def deletar_agendamento(agendamento_id):
    """Deleta agendamento"""
    conn = get_db_site()
    cur = conn.cursor()

    query = "DELETE FROM agendamentos WHERE id = %s"
    cur.execute(query, (agendamento_id,))

    conn.commit()
    cur.close()
    conn.close()


def toggle_agendamento(agendamento_id):
    """Ativa/desativa agendamento"""
    conn = get_db_site()
    cur = conn.cursor()

    query = "UPDATE agendamentos SET ativo = NOT ativo WHERE id = %s"
    cur.execute(query, (agendamento_id,))

    conn.commit()
    cur.close()
    conn.close()


def obter_logs_agendamento(agendamento_id):
    """Busca logs de envio de um agendamento"""
    conn = get_db_site()
    cur = conn.cursor()

    query = """
        SELECT 
            l.id,
            l.data_envio,
            l.status,
            l.mensagem_enviada,
            l.resposta_api,
            l.erro,
            l.criado_em,
            g.nome_grupo
        FROM agendamento_logs l
        INNER JOIN grupos_whatsapp g ON l.grupo_id = g.id
        WHERE l.agendamento_id = %s
        ORDER BY l.criado_em DESC
    """

    cur.execute(query, (agendamento_id,))
    rows = cur.fetchall()

    logs = []
    for row in rows:
        logs.append({
            'id': row[0],
            'data_envio': row[1].strftime('%d/%m/%Y %H:%M:%S') if row[1] else '',
            'status': row[2],
            'mensagem_enviada': row[3],
            'resposta_api': row[4],
            'erro': row[5],
            'criado_em': row[6].strftime('%d/%m/%Y %H:%M:%S') if row[6] else '',
            'nome_grupo': row[7]
        })

    cur.close()
    conn.close()

    return logs


def atualizar_agendamento(agendamento_id, dados):
    """Atualiza um agendamento existente"""
    conn = get_db_site()
    cur = conn.cursor()

    query = """
        UPDATE agendamentos 
        SET grupo_id = %s,
            tipo_envio = %s,
            dias_semana = %s,
            data_envio = %s,
            hora_inicio = %s,
            dia_offset_inicio = %s,
            hora_fim = %s,
            dia_offset_fim = %s,
            atualizado_em = NOW()
        WHERE id = %s
    """

    cur.execute(query, (
        dados['grupo_id'],
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
