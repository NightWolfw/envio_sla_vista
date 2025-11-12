import sqlite3
from datetime import datetime

def salvar_mensagem(grupos, mensagem, tag):
    conn = sqlite3.connect('site.db')
    cur = conn.cursor()
    for group_id in grupos:
        cur.execute("""
            INSERT INTO mensagens (grupo_id, mensagem, tag, data_envio)
            VALUES (?, ?, ?, ?)
        """, (group_id, mensagem, tag, datetime.now()))
    conn.commit()
    cur.close()
    conn.close()
    return True

def salvar_mensagem_agendada(grupos, mensagem, tag):
    conn = sqlite3.connect('site.db')
    cur = conn.cursor()
    for group_id in grupos:
        cur.execute("""
            INSERT INTO mensagens_agendadas (grupo_id, mensagem, tag, data_agendamento)
            VALUES (?, ?, ?, ?)
        """, (group_id, mensagem, tag, datetime.now()))
    conn.commit()
    cur.close()
    conn.close()
    return True

def listar_mensagens(apenas_ativas=False):
    conn = sqlite3.connect('site.db')
    cur = conn.cursor()
    query = "SELECT * FROM mensagens"
    if apenas_ativas:
        query += " WHERE data_envio IS NOT NULL"
    cur.execute(query)
    mensagens = cur.fetchall()
    cur.close()
    conn.close()
    return mensagens
