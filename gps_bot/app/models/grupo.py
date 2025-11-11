from app.models.database import get_db_site


def listar_grupos(filtro_id=None, filtro_cr=None, filtro_nome=None, filtros=None):
    """Lista grupos com filtros avançados"""
    conn = get_db_site()
    cur = conn.cursor()

    query = """
        SELECT id, group_id, nome_grupo, envio, cr,
               cliente, pec_01, pec_02,
               diretorexecutivo, diretorregional,
               gerenteregional, gerente, supervisor, dia_todo
        FROM grupos_whatsapp 
        WHERE 1=1
    """
    params = []

    # Filtros simples
    if filtro_id:
        query += " AND group_id ILIKE %s"
        params.append(f"%{filtro_id}%")

    if filtro_cr:
        query += " AND cr ILIKE %s"
        params.append(f"%{filtro_cr}%")

    if filtro_nome:
        query += " AND nome_grupo ILIKE %s"
        params.append(f"%{filtro_nome}%")

    # Filtros avançados
    if filtros:
        if filtros.get('diretor_executivo'):
            query += " AND LOWER(diretorexecutivo) LIKE LOWER(%s)"
            params.append(f"%{filtros['diretor_executivo']}%")

        if filtros.get('diretor_regional'):
            query += " AND LOWER(diretorregional) LIKE LOWER(%s)"
            params.append(f"%{filtros['diretor_regional']}%")

        if filtros.get('gerente_regional'):
            query += " AND LOWER(gerenteregional) LIKE LOWER(%s)"
            params.append(f"%{filtros['gerente_regional']}%")

        if filtros.get('gerente'):
            query += " AND LOWER(gerente) LIKE LOWER(%s)"
            params.append(f"%{filtros['gerente']}%")

        if filtros.get('supervisor'):
            query += " AND LOWER(supervisor) LIKE LOWER(%s)"
            params.append(f"%{filtros['supervisor']}%")

        if filtros.get('cliente'):
            query += " AND LOWER(cliente) LIKE LOWER(%s)"
            params.append(f"%{filtros['cliente']}%")

        if filtros.get('pec_01'):
            query += " AND LOWER(pec_01) LIKE LOWER(%s)"
            params.append(f"%{filtros['pec_01']}%")

        if filtros.get('pec_02'):
            query += " AND LOWER(pec_02) LIKE LOWER(%s)"
            params.append(f"%{filtros['pec_02']}%")

    query += " ORDER BY nome_grupo"

    cur.execute(query, params)
    grupos = cur.fetchall()
    cur.close()
    conn.close()

    return grupos


def obter_valores_unicos_filtros(apenas_ativos=False):
    """Retorna valores únicos para os dropdowns de filtros"""
    conn = get_db_site()
    cur = conn.cursor()

    filtros = {}

    # Adiciona filtro de envio se especificado
    where_clause = "WHERE {campo} IS NOT NULL"
    if apenas_ativos:
        where_clause = "WHERE {campo} IS NOT NULL AND envio = true"

    # Diretores Executivos
    cur.execute(
        f"SELECT DISTINCT diretorexecutivo FROM grupos_whatsapp {where_clause.format(campo='diretorexecutivo')} ORDER BY diretorexecutivo")
    filtros['diretor_executivo'] = [row[0] for row in cur.fetchall()]

    # Diretores Regionais
    cur.execute(
        f"SELECT DISTINCT diretorregional FROM grupos_whatsapp {where_clause.format(campo='diretorregional')} ORDER BY diretorregional")
    filtros['diretor_regional'] = [row[0] for row in cur.fetchall()]

    # Gerentes Regionais
    cur.execute(
        f"SELECT DISTINCT gerenteregional FROM grupos_whatsapp {where_clause.format(campo='gerenteregional')} ORDER BY gerenteregional")
    filtros['gerente_regional'] = [row[0] for row in cur.fetchall()]

    # Gerentes
    cur.execute(
        f"SELECT DISTINCT gerente FROM grupos_whatsapp {where_clause.format(campo='gerente')} ORDER BY gerente")
    filtros['gerente'] = [row[0] for row in cur.fetchall()]

    # Supervisores
    cur.execute(
        f"SELECT DISTINCT supervisor FROM grupos_whatsapp {where_clause.format(campo='supervisor')} ORDER BY supervisor")
    filtros['supervisor'] = [row[0] for row in cur.fetchall()]

    # Clientes
    cur.execute(
        f"SELECT DISTINCT cliente FROM grupos_whatsapp {where_clause.format(campo='cliente')} ORDER BY cliente")
    filtros['cliente'] = [row[0] for row in cur.fetchall()]

    # PEC 01
    cur.execute(
        f"SELECT DISTINCT pec_01 FROM grupos_whatsapp {where_clause.format(campo='pec_01')} ORDER BY pec_01")
    filtros['pec_01'] = [row[0] for row in cur.fetchall()]

    # PEC 02
    cur.execute(
        f"SELECT DISTINCT pec_02 FROM grupos_whatsapp {where_clause.format(campo='pec_02')} ORDER BY pec_02")
    filtros['pec_02'] = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()
    return filtros


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
        novo_envio = not grupo[3]

        conn = get_db_site()
        cur = conn.cursor()
        cur.execute("UPDATE grupos_whatsapp SET envio = %s WHERE id = %s",
                    (novo_envio, grupo_id))
        conn.commit()
        cur.close()
        conn.close()

        return novo_envio
    return None


def deletar_grupos_massa(grupo_ids):
    """Deleta múltiplos grupos de uma vez"""
    conn = get_db_site()
    cur = conn.cursor()

    # Converte IDs para tupla
    placeholders = ','.join(['%s'] * len(grupo_ids))

    cur.execute(f"DELETE FROM grupos_whatsapp WHERE id IN ({placeholders})", grupo_ids)

    deletados = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    return deletados
