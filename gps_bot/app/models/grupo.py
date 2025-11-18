from app.models.database import get_db_site


def listar_grupos(filtros=None):
    """Lista grupos com filtros opcionais"""
    conn = get_db_site()
    cur = conn.cursor()

    query = """
        SELECT id, group_id, nome_grupo, envio, cr, cliente, pec_01, pec_02,
               diretorexecutivo, diretorregional, gerenteregional, gerente,
               supervisor
        FROM grupos_whatsapp
        WHERE 1=1
    """
    params = []

    if filtros:
        # ✅ Filtro por ID
        if 'id' in filtros and filtros['id']:
            query += " AND id = %s"
            params.append(filtros['id'])

        # ✅ Filtro por Nome (busca parcial)
        if 'nome' in filtros and filtros['nome']:
            query += " AND LOWER(nome_grupo) LIKE %s"
            params.append(f"%{filtros['nome'].lower()}%")

        # ✅ Filtro por CR
        if 'cr' in filtros and filtros['cr']:
            query += " AND cr = %s"
            params.append(filtros['cr'])

        # Filtro por envio
        if 'envio' in filtros:
            query += " AND envio = %s"
            params.append(filtros['envio'])

        # Filtros de hierarquia
        if 'diretorexecutivo' in filtros and filtros['diretorexecutivo']:
            query += " AND diretorexecutivo = %s"
            params.append(filtros['diretorexecutivo'])

        if 'diretorregional' in filtros and filtros['diretorregional']:
            query += " AND diretorregional = %s"
            params.append(filtros['diretorregional'])

        if 'gerenteregional' in filtros and filtros['gerenteregional']:
            query += " AND gerenteregional = %s"
            params.append(filtros['gerenteregional'])

        if 'gerente' in filtros and filtros['gerente']:
            query += " AND gerente = %s"
            params.append(filtros['gerente'])

        if 'supervisor' in filtros and filtros['supervisor']:
            query += " AND supervisor = %s"
            params.append(filtros['supervisor'])

        if 'cliente' in filtros and filtros['cliente']:
            query += " AND cliente = %s"
            params.append(filtros['cliente'])

        if 'pec_01' in filtros and filtros['pec_01']:
            query += " AND pec_01 = %s"
            params.append(filtros['pec_01'])

        if 'pec_02' in filtros and filtros['pec_02']:
            query += " AND pec_02 = %s"
            params.append(filtros['pec_02'])

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

    query = """
        SELECT id, group_id, nome_grupo, envio, cr, cliente, pec_01, pec_02,
               diretorexecutivo, diretorregional, gerenteregional, gerente,
               supervisor
        FROM grupos_whatsapp
        WHERE id = %s
    """

    cur.execute(query, (grupo_id,))
    grupo = cur.fetchone()
    cur.close()
    conn.close()

    return grupo


def buscar_crs_por_grupos(grupos_ids):
    """Busca os CRs correspondentes aos grupos selecionados"""
    if not grupos_ids:
        return []

    conn = get_db_site()
    cur = conn.cursor()

    # Converte para lista se for string
    if isinstance(grupos_ids, str):
        grupos_ids = [grupos_ids]

    # Cria placeholders para a query
    placeholders = ','.join(['%s'] * len(grupos_ids))
    query = f"""
        SELECT DISTINCT cr
        FROM grupos_whatsapp
        WHERE group_id IN ({placeholders})
        AND cr IS NOT NULL
    """

    cur.execute(query, tuple(grupos_ids))
    crs = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return crs


def obter_valores_unicos_filtros(apenas_ativos=False):
    """Retorna valores únicos para os filtros avançados dos grupos"""
    conn = get_db_site()
    cur = conn.cursor()

    where = ""
    if apenas_ativos:
        where = "WHERE envio = TRUE"

    # Nomes de campos SEM underscore (como estão no banco)
    campos = [
        "diretorexecutivo",
        "diretorregional",
        "gerenteregional",
        "gerente",
        "supervisor",
        "cliente",
        "pec_01",
        "pec_02"
    ]

    # Mapeamento para as chaves do dicionário (com underscore para o template)
    mapeamento = {
        "diretorexecutivo": "diretor_executivo",
        "diretorregional": "diretor_regional",
        "gerenteregional": "gerente_regional",
        "gerente": "gerente",
        "supervisor": "supervisor",
        "cliente": "cliente",
        "pec_01": "pec_01",
        "pec_02": "pec_02"
    }

    filtros = {}
    for campo in campos:
        if where:
            query = f"SELECT DISTINCT {campo} FROM grupos_whatsapp {where} AND {campo} IS NOT NULL ORDER BY {campo}"
        else:
            query = f"SELECT DISTINCT {campo} FROM grupos_whatsapp WHERE {campo} IS NOT NULL ORDER BY {campo}"

        cur.execute(query)
        valores = [row[0] for row in cur.fetchall() if row[0]]
        # Usa o mapeamento para criar as chaves com underscore
        filtros[mapeamento[campo]] = valores

    cur.close()
    conn.close()
    return filtros


def atualizar_grupo(grupo_id, dados):
    """Atualiza dados de um grupo"""
    conn = get_db_site()
    cur = conn.cursor()

    # ✅ CORRIGIDO: Usa os nomes CORRETOS das colunas
    query = """
        UPDATE grupos_whatsapp 
        SET group_id = %s, 
            nome_grupo = %s, 
            envio = %s, 
            cr = %s
        WHERE id = %s
    """

    cur.execute(query, (
        dados['group_id'],
        dados['nome'],
        dados['enviar_mensagem'],
        dados['cr'],
        grupo_id
    ))

    conn.commit()
    cur.close()
    conn.close()


def listar_ids_com_cr():
    """Retorna IDs dos grupos que possuem CR definido."""
    conn = get_db_site()
    cur = conn.cursor()
    cur.execute("SELECT id, nome_grupo, cr FROM grupos_whatsapp WHERE cr IS NOT NULL AND cr != '' ORDER BY nome_grupo")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def deletar_grupos_por_ids(ids):
    """Remove grupos pelo ID."""
    if not ids:
        return 0
    conn = get_db_site()
    cur = conn.cursor()
    placeholders = ",".join(["%s"] * len(ids))
    cur.execute(f"DELETE FROM grupos_whatsapp WHERE id IN ({placeholders})", tuple(ids))
    removidos = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return removidos
