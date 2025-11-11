from app.models.database import get_db_site


def listar_grupos(filtros=None):
    """Lista grupos com filtros opcionais"""
    conn = get_db_site()
    cur = conn.cursor()

    query = """
        SELECT id, group_id, nome_grupo, envio, cr, cliente, 
               pec_01, pec_02, diretorexecutivo, dia_todo
        FROM grupos_whatsapp 
        WHERE 1=1
    """
    params = []

    if filtros:
        if filtros.get('filtro_id'):
            query += " AND group_id ILIKE %s"
            params.append(f"%{filtros['filtro_id']}%")

        if filtros.get('filtro_cr'):
            query += " AND cr ILIKE %s"
            params.append(f"%{filtros['filtro_cr']}%")

        if filtros.get('filtro_nome'):
            query += " AND nome_grupo ILIKE %s"
            params.append(f"%{filtros['filtro_nome']}%")

    query += " ORDER BY nome_grupo"

    cur.execute(query, params)
    grupos = cur.fetchall()
    cur.close()
    conn.close()

    return grupos


def obter_grupo(grupo_id):
    """Busca grupo específico por ID"""
    conn = get_db_site()
    cur = conn.cursor()

    cur.execute("SELECT * FROM grupos_whatsapp WHERE id = %s", (grupo_id,))
    grupo = cur.fetchone()

    cur.close()
    conn.close()
    return grupo


def atualizar_grupo(grupo_id, dados):
    """Atualiza dados do grupo"""
    conn = get_db_site()
    cur = conn.cursor()

    cur.execute("""
        UPDATE grupos_whatsapp 
        SET group_id = %s, nome_grupo = %s, envio = %s, 
            dia_todo = %s, cr = %s
        WHERE id = %s
    """, (dados['group_id'], dados['nome_grupo'], dados['envio'],
          dados['dia_todo'], dados['cr'], grupo_id))

    conn.commit()
    cur.close()
    conn.close()


def deletar_grupo(grupo_id):
    """Deleta grupo do banco"""
    conn = get_db_site()
    cur = conn.cursor()

    cur.execute("DELETE FROM grupos_whatsapp WHERE id = %s", (grupo_id,))

    conn.commit()
    cur.close()
    conn.close()


def toggle_envio(grupo_id):
    """Ativa/desativa envio do grupo"""
    grupo = obter_grupo(grupo_id)
    if grupo:
        novo_envio = not grupo[3]  # coluna envio

        conn = get_db_site()
        cur = conn.cursor()
        cur.execute("UPDATE grupos_whatsapp SET envio = %s WHERE id = %s",
                    (novo_envio, grupo_id))
        conn.commit()
        cur.close()
        conn.close()

        return novo_envio
    return None
