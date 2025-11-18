from datetime import datetime
from typing import Any, Dict, List, Tuple

import pytz

from app.models.database import get_db_site

# Timezone de Brasília
TIMEZONE_BRASILIA = pytz.timezone('America/Sao_Paulo')

AGENDAMENTO_COLUMNS = [
    'id',
    'grupo_id',
    'tipo_envio',
    'dias_semana',
    'data_envio',
    'hora_inicio',
    'dia_offset_inicio',
    'hora_fim',
    'dia_offset_fim',
    'ativo',
    'proximo_envio',
    'criado_em',
    'atualizado_em'
]


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


def listar_agendamentos_filtrado(filtros: Dict[str, Any], page: int, page_size: int) -> Tuple[List[Dict[str, Any]], int]:
    """Lista agendamentos com filtros e paginação"""
    conn = get_db_site()
    cur = conn.cursor()

    where_clauses = []
    params: List[Any] = []

    if filtros.get('tipo_envio'):
        where_clauses.append("a.tipo_envio = %s")
        params.append(filtros['tipo_envio'])

    if filtros.get('ativo') is not None:
        where_clauses.append("a.ativo = %s")
        params.append(filtros['ativo'])

    if filtros.get('grupo'):
        where_clauses.append("LOWER(g.nome_grupo) LIKE %s")
        params.append(f"%{filtros['grupo'].lower()}%")

    if filtros.get('cr'):
        where_clauses.append("g.cr ILIKE %s")
        params.append(f"%{filtros['cr']}%")

    if filtros.get('dia'):
        where_clauses.append("a.dias_semana ILIKE %s")
        params.append(f"%{filtros['dia']}%")

    if filtros.get('data_inicio'):
        where_clauses.append("a.data_envio >= %s")
        params.append(filtros['data_inicio'])

    if filtros.get('data_fim'):
        where_clauses.append("a.data_envio <= %s")
        params.append(filtros['data_fim'])

    where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    count_query = f"""
        SELECT COUNT(*)
        FROM agendamentos a
        INNER JOIN grupos_whatsapp g ON a.grupo_id = g.id
        {where_clause}
    """
    cur.execute(count_query, params)
    total = cur.fetchone()[0]

    offset = (page - 1) * page_size
    data_query = f"""
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
            a.criado_em,
            a.atualizado_em,
            last_log.status as ultimo_status,
            last_log.data_envio as ultimo_envio,
            last_log.erro as ultimo_erro
        FROM agendamentos a
        INNER JOIN grupos_whatsapp g ON a.grupo_id = g.id
        LEFT JOIN LATERAL (
            SELECT 
                l.status,
                l.data_envio,
                l.erro
            FROM agendamento_logs l
            WHERE l.agendamento_id = a.id
            ORDER BY l.criado_em DESC
            LIMIT 1
        ) AS last_log ON TRUE
        {where_clause}
        ORDER BY a.criado_em DESC
        LIMIT %s OFFSET %s
    """
    query_params = params + [page_size, offset]
    cur.execute(data_query, query_params)
    rows = cur.fetchall()

    itens = []
    for row in rows:
        data_envio = row[6]
        if data_envio:
            if data_envio.tzinfo is None:
                data_envio = TIMEZONE_BRASILIA.localize(data_envio)
            else:
                data_envio = data_envio.astimezone(TIMEZONE_BRASILIA)
        itens.append({
            'id': row[0],
            'grupo_id': row[1],
            'nome_grupo': row[2],
            'cr': row[3],
            'tipo_envio': row[4],
            'dias_semana': row[5],
            'data_envio': data_envio,
            'proximo_envio': data_envio.strftime('%d/%m/%Y %H:%M') if data_envio else None,
            'hora_inicio': row[7],
            'dia_offset_inicio': row[8],
            'hora_fim': row[9],
            'dia_offset_fim': row[10],
            'ativo': row[11],
            'criado_em': row[12],
            'atualizado_em': row[13],
            'ultimo_status': row[14],
            'ultimo_envio': row[15].strftime('%d/%m/%Y %H:%M:%S') if row[15] else None,
            'ultimo_erro': row[16]
        })

    cur.close()
    conn.close()

    return itens, total


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


def obter_logs_agendamento(agendamento_id, page: int = 1, page_size: int = 20):
    """Busca logs de envio de um agendamento com paginação"""
    conn = get_db_site()
    cur = conn.cursor()

    count_query = """
        SELECT COUNT(*) FROM agendamento_logs WHERE agendamento_id = %s
    """
    cur.execute(count_query, (agendamento_id,))
    total = cur.fetchone()[0]

    offset = (page - 1) * page_size

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
        LIMIT %s OFFSET %s
    """

    cur.execute(query, (agendamento_id, page_size, offset))
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

    return logs, total


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


def definir_status_agendamento(agendamento_id: int, ativo: bool) -> None:
    conn = get_db_site()
    cur = conn.cursor()
    query = """
        UPDATE agendamentos
        SET ativo = %s,
            atualizado_em = NOW()
        WHERE id = %s
    """
    cur.execute(query, (ativo, agendamento_id))
    conn.commit()
    cur.close()
    conn.close()


def clonar_agendamento(agendamento_id: int) -> int:
    registro = obter_agendamento(agendamento_id)
    if not registro:
        raise ValueError("Agendamento não encontrado para clonagem")
    data = dict(zip(AGENDAMENTO_COLUMNS, registro))
    novo = {
        'grupo_id': data['grupo_id'],
        'tipo_envio': data['tipo_envio'],
        'dias_semana': data['dias_semana'],
        'data_envio': data['data_envio'],
        'hora_inicio': data['hora_inicio'],
        'dia_offset_inicio': data['dia_offset_inicio'],
        'hora_fim': data['hora_fim'],
        'dia_offset_fim': data['dia_offset_fim']
    }
    return criar_agendamento(novo)
