"""
Model para gestão de logs de envio
"""
from app.models.database import get_db_site


def registrar_envio(mensagem_agendada_id, group_id, nome_grupo, mensagem, status, erro_detalhe=None):
    """Registra um envio no log"""
    conn = get_db_site()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO log_envios 
        (mensagem_agendada_id, group_id, nome_grupo, mensagem, status, erro_detalhe)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (mensagem_agendada_id, group_id, nome_grupo, mensagem, status, erro_detalhe))

    log_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return log_id


def listar_logs(mensagem_id=None, status=None, limit=100, offset=0):
    """Lista logs de envio com filtros opcionais"""
    conn = get_db_site()
    cur = conn.cursor()

    query = "SELECT * FROM log_envios WHERE 1=1"
    params = []

    if mensagem_id:
        query += " AND mensagem_agendada_id = %s"
        params.append(mensagem_id)

    if status:
        query += " AND status = %s"
        params.append(status)

    query += " ORDER BY enviado_em DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cur.execute(query, params)
    logs = cur.fetchall()
    cur.close()
    conn.close()

    return logs


def obter_log(log_id):
    """Busca log específico"""
    conn = get_db_site()
    cur = conn.cursor()

    cur.execute("SELECT * FROM log_envios WHERE id = %s", (log_id,))
    log = cur.fetchone()

    cur.close()
    conn.close()
    return log


def contar_logs(mensagem_id=None, status=None):
    """Conta total de logs (para paginação)"""
    conn = get_db_site()
    cur = conn.cursor()

    query = "SELECT COUNT(*) FROM log_envios WHERE 1=1"
    params = []

    if mensagem_id:
        query += " AND mensagem_agendada_id = %s"
        params.append(mensagem_id)

    if status:
        query += " AND status = %s"
        params.append(status)

    cur.execute(query, params)
    total = cur.fetchone()[0]

    cur.close()
    conn.close()
    return total


def obter_estatisticas_envio(mensagem_id=None):
    """Retorna estatísticas de envios (sucessos, erros, total)"""
    conn = get_db_site()
    cur = conn.cursor()

    query = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'SUCESSO' THEN 1 ELSE 0 END) as sucessos,
            SUM(CASE WHEN status = 'ERRO' THEN 1 ELSE 0 END) as erros
        FROM log_envios
        WHERE 1=1
    """
    params = []

    if mensagem_id:
        query += " AND mensagem_agendada_id = %s"
        params.append(mensagem_id)

    cur.execute(query, params)
    resultado = cur.fetchone()

    cur.close()
    conn.close()

    return {
        'total': resultado[0] or 0,
        'sucessos': resultado[1] or 0,
        'erros': resultado[2] or 0
    }


def limpar_logs_antigos(dias=30):
    """Remove logs mais antigos que X dias"""
    conn = get_db_site()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM log_envios 
        WHERE enviado_em < NOW() - INTERVAL '%s days'
    """, (dias,))

    linhas_deletadas = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    return linhas_deletadas
