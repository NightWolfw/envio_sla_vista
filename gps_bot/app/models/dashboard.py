"""
Model para Dashboard SLA
Consultas otimizadas usando COUNT() para não sobrecarregar o banco
"""
from app.models.database import get_db_vista
from datetime import datetime, timedelta
import calendar


def buscar_resumo_tarefas(filtros, data_inicio, data_fim):
    """
    Retorna contadores de tarefas por status (cards de resumo)
    Usa COUNT() para performance
    """
    conn = get_db_vista()
    cur = conn.cursor()
    
    # Monta WHERE dinâmico com filtros
    where_clauses = []
    params = [data_inicio, data_fim]
    
    where_clauses.append("t.disponibilizacao >= %s")
    where_clauses.append("t.disponibilizacao <= %s")
    where_clauses.append("t.status IN (10, 25, 85)")
    
    # Aplica filtros
    if filtros.get('cr'):
        where_clauses.append("e.crno = %s")
        params.append(filtros['cr'])
    
    if filtros.get('cliente'):
        where_clauses.append("e.cliente = %s")
        params.append(filtros['cliente'])
    
    # Filtros de gestores via dm_cr
    filtros_gestores = []
    if filtros.get('diretor_executivo'):
        filtros_gestores.append("cr.diretorexecutivo = %s")
        params.append(filtros['diretor_executivo'])
    
    if filtros.get('diretor_regional'):
        filtros_gestores.append("cr.diretorregional = %s")
        params.append(filtros['diretor_regional'])
    
    if filtros.get('gerente_regional'):
        filtros_gestores.append("cr.gerenteregional = %s")
        params.append(filtros['gerente_regional'])
    
    if filtros.get('gerente'):
        filtros_gestores.append("cr.gerente = %s")
        params.append(filtros['gerente'])
    
    if filtros.get('supervisor'):
        filtros_gestores.append("cr.supervisor = %s")
        params.append(filtros['supervisor'])
    
    if filtros.get('pec_01'):
        where_clauses.append("e.nivel_01 = %s")
        params.append(filtros['pec_01'])
    
    if filtros.get('pec_02'):
        where_clauses.append("e.nivel_02 = %s")
        params.append(filtros['pec_02'])
    
    where_sql = " AND ".join(where_clauses)
    
    # JOIN com dm_cr apenas se tiver filtros de gestores
    join_cr = ""
    if filtros_gestores:
        join_cr = "LEFT JOIN dw_vista.dm_cr cr ON e.id_cr = cr.id_cr"
        where_sql += " AND (" + " AND ".join(filtros_gestores) + ")"
    
    query = f"""
        SELECT 
            t.status,
            t.expirada,
            COUNT(*) as total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        {join_cr}
        WHERE {where_sql}
        GROUP BY t.status, t.expirada
    """
    
    cur.execute(query, params)
    resultados = cur.fetchall()
    
    # Inicializa contadores
    stats = {
        'finalizadas': 0,
        'nao_realizadas': 0,
        'em_aberto': 0,
        'iniciadas': 0
    }
    
    # Preenche com resultados
    for row in resultados:
        status = row[0]
        expirada = row[1]
        total = row[2]
        
        if status == 85 and expirada == False:
            stats['finalizadas'] = total
        elif status == 85 and expirada == True:
            stats['nao_realizadas'] = total
        elif status == 10:
            stats['em_aberto'] = total
        elif status == 25:
            stats['iniciadas'] = total
    
    cur.close()
    conn.close()
    
    return stats


def buscar_tarefas_por_dia_mes(filtros, mes, ano):
    """
    Retorna tarefas agrupadas por dia do mês separadas por status (para gráfico de colunas empilhadas)
    Retorna 4 séries: finalizadas, não realizadas, em aberto, iniciadas
    """
    conn = get_db_vista()
    cur = conn.cursor()
    
    # Primeiro e último dia do mês
    primeiro_dia = datetime(ano, mes, 1)
    ultimo_dia = datetime(ano, mes, calendar.monthrange(ano, mes)[1], 23, 59, 59)
    
    # Monta WHERE dinâmico
    where_clauses = ["t.disponibilizacao >= %s", "t.disponibilizacao <= %s", "t.status IN (10, 25, 85)"]
    params = [primeiro_dia, ultimo_dia]
    
    # Aplica filtros (mesma lógica do resumo)
    filtros_gestores = []
    
    if filtros.get('cr'):
        where_clauses.append("e.crno = %s")
        params.append(filtros['cr'])
    
    if filtros.get('cliente'):
        where_clauses.append("e.cliente = %s")
        params.append(filtros['cliente'])
    
    if filtros.get('diretor_executivo'):
        filtros_gestores.append("cr.diretorexecutivo = %s")
        params.append(filtros['diretor_executivo'])
    
    if filtros.get('diretor_regional'):
        filtros_gestores.append("cr.diretorregional = %s")
        params.append(filtros['diretor_regional'])
    
    if filtros.get('gerente_regional'):
        filtros_gestores.append("cr.gerenteregional = %s")
        params.append(filtros['gerente_regional'])
    
    if filtros.get('gerente'):
        filtros_gestores.append("cr.gerente = %s")
        params.append(filtros['gerente'])
    
    if filtros.get('supervisor'):
        filtros_gestores.append("cr.supervisor = %s")
        params.append(filtros['supervisor'])
    
    if filtros.get('pec_01'):
        where_clauses.append("e.nivel_01 = %s")
        params.append(filtros['pec_01'])
    
    if filtros.get('pec_02'):
        where_clauses.append("e.nivel_02 = %s")
        params.append(filtros['pec_02'])
    
    where_sql = " AND ".join(where_clauses)
    
    join_cr = ""
    if filtros_gestores:
        join_cr = "LEFT JOIN dw_vista.dm_cr cr ON e.id_cr = cr.id_cr"
        where_sql += " AND (" + " AND ".join(filtros_gestores) + ")"
    
    query = f"""
        SELECT 
            DATE(t.disponibilizacao) as dia,
            SUM(CASE WHEN t.status = 85 AND t.expirada = FALSE THEN 1 ELSE 0 END) as finalizadas,
            SUM(CASE WHEN t.status = 85 AND t.expirada = TRUE THEN 1 ELSE 0 END) as nao_realizadas,
            SUM(CASE WHEN t.status = 10 THEN 1 ELSE 0 END) as em_aberto,
            SUM(CASE WHEN t.status = 25 THEN 1 ELSE 0 END) as iniciadas
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        {join_cr}
        WHERE {where_sql}
        GROUP BY DATE(t.disponibilizacao)
        ORDER BY dia
    """
    
    cur.execute(query, params)
    resultados = cur.fetchall()
    
    # Cria dicionário com os dados do banco por dia
    dados_banco = {}
    for row in resultados:
        dia_numero = row[0].day
        dados_banco[dia_numero] = {
            'finalizadas': row[1],
            'nao_realizadas': row[2],
            'em_aberto': row[3],
            'iniciadas': row[4]
        }
    
    # Preenche todos os dias do mês (1 até último dia)
    ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
    dados = []
    
    for dia in range(1, ultimo_dia_mes + 1):
        data_completa = datetime(ano, mes, dia)
        dia_dados = dados_banco.get(dia, {'finalizadas': 0, 'nao_realizadas': 0, 'em_aberto': 0, 'iniciadas': 0})
        
        dados.append({
            'dia': data_completa.strftime('%Y-%m-%d'),
            'finalizadas': dia_dados['finalizadas'],
            'nao_realizadas': dia_dados['nao_realizadas'],
            'em_aberto': dia_dados['em_aberto'],
            'iniciadas': dia_dados['iniciadas']
        })
    
    cur.close()
    conn.close()
    
    return dados


def buscar_heatmap_realizacao(filtros, data_inicio, data_fim):
    """
    Retorna porcentagem de realização por CR (heatmap)
    Verde (>90%), Amarelo (65-90%), Vermelho (<65%)
    """
    conn = get_db_vista()
    cur = conn.cursor()
    
    where_clauses = ["t.disponibilizacao >= %s", "t.disponibilizacao <= %s", "t.status IN (10, 25, 85)"]
    params = [data_inicio, data_fim]
    
    # Aplica filtros
    filtros_gestores = []
    
    if filtros.get('cr'):
        where_clauses.append("e.crno = %s")
        params.append(filtros['cr'])
    
    if filtros.get('cliente'):
        where_clauses.append("e.cliente = %s")
        params.append(filtros['cliente'])
    
    if filtros.get('diretor_executivo'):
        filtros_gestores.append("cr.diretorexecutivo = %s")
        params.append(filtros['diretor_executivo'])
    
    if filtros.get('diretor_regional'):
        filtros_gestores.append("cr.diretorregional = %s")
        params.append(filtros['diretor_regional'])
    
    if filtros.get('gerente_regional'):
        filtros_gestores.append("cr.gerenteregional = %s")
        params.append(filtros['gerente_regional'])
    
    if filtros.get('gerente'):
        filtros_gestores.append("cr.gerente = %s")
        params.append(filtros['gerente'])
    
    if filtros.get('supervisor'):
        filtros_gestores.append("cr.supervisor = %s")
        params.append(filtros['supervisor'])
    
    if filtros.get('pec_01'):
        where_clauses.append("e.nivel_01 = %s")
        params.append(filtros['pec_01'])
    
    if filtros.get('pec_02'):
        where_clauses.append("e.nivel_02 = %s")
        params.append(filtros['pec_02'])
    
    where_sql = " AND ".join(where_clauses)
    
    join_cr = ""
    if filtros_gestores:
        join_cr = "LEFT JOIN dw_vista.dm_cr cr ON e.id_cr = cr.id_cr"
        where_sql += " AND (" + " AND ".join(filtros_gestores) + ")"
    
    query = f"""
        SELECT 
            e.crno as cr,
            e.nivel_03 as contrato,
            SUM(CASE WHEN t.status = 85 AND t.expirada = FALSE THEN 1 ELSE 0 END) as finalizadas,
            SUM(CASE WHEN t.status = 85 AND t.expirada = TRUE THEN 1 ELSE 0 END) as nao_realizadas,
            SUM(CASE WHEN t.status = 10 THEN 1 ELSE 0 END) as em_aberto,
            SUM(CASE WHEN t.status = 25 THEN 1 ELSE 0 END) as iniciadas,
            COUNT(*) as total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        {join_cr}
        WHERE {where_sql}
        GROUP BY e.crno, e.nivel_03
        HAVING COUNT(*) > 0
        ORDER BY e.crno
    """
    
    cur.execute(query, params)
    resultados = cur.fetchall()
    
    # Calcula porcentagem e cor
    dados = []
    for row in resultados:
        cr, contrato, finalizadas, nao_realizadas, em_aberto, iniciadas, total = row
        
        # Calcula porcentagem de realização
        if total > 0:
            porcentagem = (finalizadas / total) * 100
        else:
            porcentagem = 0
        
        # Define cor
        if porcentagem > 90:
            cor = 'verde'
            cor_hex = '#28a745'
        elif porcentagem >= 65:
            cor = 'amarelo'
            cor_hex = '#ffc107'
        else:
            cor = 'vermelho'
            cor_hex = '#dc3545'
        
        dados.append({
            'cr': cr,
            'contrato': contrato,
            'finalizadas': finalizadas,
            'nao_realizadas': nao_realizadas,
            'em_aberto': em_aberto,
            'iniciadas': iniciadas,
            'total': total,
            'porcentagem': round(porcentagem, 2),
            'cor': cor,
            'cor_hex': cor_hex
        })
    
    cur.close()
    conn.close()
    
    return dados


def buscar_top_executores(filtros, data_inicio, data_fim, limit=10):
    """
    Retorna TOP executores por quantidade de tarefas finalizadas
    """
    conn = get_db_vista()
    cur = conn.cursor()
    
    where_clauses = ["t.disponibilizacao >= %s", "t.disponibilizacao <= %s", "t.status = 85", "t.expirada = FALSE"]
    params = [data_inicio, data_fim]
    
    # Aplica filtros
    filtros_gestores = []
    
    if filtros.get('cr'):
        where_clauses.append("e.crno = %s")
        params.append(filtros['cr'])
    
    if filtros.get('cliente'):
        where_clauses.append("e.cliente = %s")
        params.append(filtros['cliente'])
    
    if filtros.get('diretor_executivo'):
        filtros_gestores.append("cr.diretorexecutivo = %s")
        params.append(filtros['diretor_executivo'])
    
    if filtros.get('diretor_regional'):
        filtros_gestores.append("cr.diretorregional = %s")
        params.append(filtros['diretor_regional'])
    
    if filtros.get('gerente_regional'):
        filtros_gestores.append("cr.gerenteregional = %s")
        params.append(filtros['gerente_regional'])
    
    if filtros.get('gerente'):
        filtros_gestores.append("cr.gerente = %s")
        params.append(filtros['gerente'])
    
    if filtros.get('supervisor'):
        filtros_gestores.append("cr.supervisor = %s")
        params.append(filtros['supervisor'])
    
    if filtros.get('pec_01'):
        where_clauses.append("e.nivel_01 = %s")
        params.append(filtros['pec_01'])
    
    if filtros.get('pec_02'):
        where_clauses.append("e.nivel_02 = %s")
        params.append(filtros['pec_02'])
    
    where_sql = " AND ".join(where_clauses)
    
    join_cr = ""
    if filtros_gestores:
        join_cr = "LEFT JOIN dw_vista.dm_cr cr ON e.id_cr = cr.id_cr"
        where_sql += " AND (" + " AND ".join(filtros_gestores) + ")"
    
    # Limit SQL
    limit_sql = "" if limit == 0 else f"LIMIT {limit}"
    
    query = f"""
        SELECT 
            COALESCE(r.nome, 'Sem Executor') as executor,
            COUNT(*) as total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        LEFT JOIN dbo.recurso r ON t.finalizadoporhash = r.codigohash
        {join_cr}
        WHERE {where_sql}
        GROUP BY executor
        HAVING COUNT(*) > 0
        ORDER BY total DESC
        {limit_sql}
    """
    
    cur.execute(query, params)
    resultados = cur.fetchall()
    
    dados = []
    for row in resultados:
        dados.append({
            'executor': row[0],
            'total': row[1]
        })
    
    cur.close()
    conn.close()
    
    return dados


def buscar_top_locais(filtros, data_inicio, data_fim, limit=10):
    """
    Retorna TOP locais por quantidade de tarefas
    """
    conn = get_db_vista()
    cur = conn.cursor()
    
    where_clauses = ["t.disponibilizacao >= %s", "t.disponibilizacao <= %s", "t.status IN (10, 25, 85)"]
    params = [data_inicio, data_fim]
    
    # Aplica filtros
    filtros_gestores = []
    
    if filtros.get('cr'):
        where_clauses.append("e.crno = %s")
        params.append(filtros['cr'])
    
    if filtros.get('cliente'):
        where_clauses.append("e.cliente = %s")
        params.append(filtros['cliente'])
    
    if filtros.get('diretor_executivo'):
        filtros_gestores.append("cr.diretorexecutivo = %s")
        params.append(filtros['diretor_executivo'])
    
    if filtros.get('diretor_regional'):
        filtros_gestores.append("cr.diretorregional = %s")
        params.append(filtros['diretor_regional'])
    
    if filtros.get('gerente_regional'):
        filtros_gestores.append("cr.gerenteregional = %s")
        params.append(filtros['gerente_regional'])
    
    if filtros.get('gerente'):
        filtros_gestores.append("cr.gerente = %s")
        params.append(filtros['gerente'])
    
    if filtros.get('supervisor'):
        filtros_gestores.append("cr.supervisor = %s")
        params.append(filtros['supervisor'])
    
    if filtros.get('pec_01'):
        where_clauses.append("e.nivel_01 = %s")
        params.append(filtros['pec_01'])
    
    if filtros.get('pec_02'):
        where_clauses.append("e.nivel_02 = %s")
        params.append(filtros['pec_02'])
    
    where_sql = " AND ".join(where_clauses)
    
    join_cr = ""
    if filtros_gestores:
        join_cr = "LEFT JOIN dw_vista.dm_cr cr ON e.id_cr = cr.id_cr"
        where_sql += " AND (" + " AND ".join(filtros_gestores) + ")"
    
    limit_sql = "" if limit == 0 else f"LIMIT {limit}"
    
    query = f"""
        SELECT 
            COALESCE(
                NULLIF(CONCAT_WS('/', 
                    NULLIF(e.nivel_05, ''), 
                    NULLIF(e.nivel_06, ''), 
                    NULLIF(e.nivel_07, '')
                ), ''),
                'N/A'
            ) AS local,
            COUNT(*) as total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        {join_cr}
        WHERE {where_sql}
        GROUP BY local
        HAVING COUNT(*) > 0
        ORDER BY total DESC
        {limit_sql}
    """
    
    cur.execute(query, params)
    resultados = cur.fetchall()
    
    dados = []
    for row in resultados:
        dados.append({
            'local': row[0],
            'total': row[1]
        })
    
    cur.close()
    conn.close()
    
    return dados


def buscar_distribuicao_status(filtros, data_inicio, data_fim):
    """
    Retorna distribuição de tarefas por status (para gráfico de pizza)
    """
    stats = buscar_resumo_tarefas(filtros, data_inicio, data_fim)
    
    dados = [
        {'status': 'Finalizadas', 'total': stats['finalizadas'], 'cor': '#28a745'},
        {'status': 'Não Realizadas', 'total': stats['nao_realizadas'], 'cor': '#dc3545'},
        {'status': 'Em Aberto', 'total': stats['em_aberto'], 'cor': '#17a2b8'},
        {'status': 'Iniciadas', 'total': stats['iniciadas'], 'cor': '#ffc107'}
    ]
    
    return dados


def buscar_heatmap_por_dia(filtros, mes, ano):
    """
    Retorna heatmap com CR x Dias do Mês
    Cada célula contém a porcentagem de tarefas finalizadas no dia
    """
    conn = get_db_vista()
    cur = conn.cursor()
    
    # Primeiro e último dia do mês
    primeiro_dia = datetime(ano, mes, 1)
    ultimo_dia = datetime(ano, mes, calendar.monthrange(ano, mes)[1], 23, 59, 59)
    
    where_clauses = ["t.disponibilizacao >= %s", "t.disponibilizacao <= %s", "t.status IN (10, 25, 85)"]
    params = [primeiro_dia, ultimo_dia]
    
    # Aplica filtros
    filtros_gestores = []
    
    if filtros.get('cr'):
        where_clauses.append("e.crno = %s")
        params.append(filtros['cr'])
    
    if filtros.get('cliente'):
        where_clauses.append("e.cliente = %s")
        params.append(filtros['cliente'])
    
    if filtros.get('diretor_executivo'):
        filtros_gestores.append("cr.diretorexecutivo = %s")
        params.append(filtros['diretor_executivo'])
    
    if filtros.get('diretor_regional'):
        filtros_gestores.append("cr.diretorregional = %s")
        params.append(filtros['diretor_regional'])
    
    if filtros.get('gerente_regional'):
        filtros_gestores.append("cr.gerenteregional = %s")
        params.append(filtros['gerente_regional'])
    
    if filtros.get('gerente'):
        filtros_gestores.append("cr.gerente = %s")
        params.append(filtros['gerente'])
    
    if filtros.get('supervisor'):
        filtros_gestores.append("cr.supervisor = %s")
        params.append(filtros['supervisor'])
    
    if filtros.get('pec_01'):
        where_clauses.append("e.nivel_01 = %s")
        params.append(filtros['pec_01'])
    
    if filtros.get('pec_02'):
        where_clauses.append("e.nivel_02 = %s")
        params.append(filtros['pec_02'])
    
    where_sql = " AND ".join(where_clauses)
    
    join_cr = ""
    if filtros_gestores:
        join_cr = "LEFT JOIN dw_vista.dm_cr cr ON e.id_cr = cr.id_cr"
        where_sql += " AND (" + " AND ".join(filtros_gestores) + ")"
    
    query = f"""
        SELECT 
            e.crno as cr,
            e.nivel_03 as contrato,
            EXTRACT(DAY FROM t.disponibilizacao) as dia,
            SUM(CASE WHEN t.status = 85 AND t.expirada = FALSE THEN 1 ELSE 0 END) as finalizadas,
            COUNT(*) as total
        FROM dbo.tarefa t
        INNER JOIN dw_vista.dm_estrutura e ON t.estruturaid = e.id_estrutura
        {join_cr}
        WHERE {where_sql}
        GROUP BY e.crno, e.nivel_03, EXTRACT(DAY FROM t.disponibilizacao)
        HAVING COUNT(*) > 0
        ORDER BY e.crno, e.nivel_03
    """
    
    cur.execute(query, params)
    resultados = cur.fetchall()
    
    # Agrupa por CR/Contrato
    dados_agrupados = {}
    for row in resultados:
        cr, contrato, dia, finalizadas, total = row
        chave = f"{cr}|{contrato}"
        
        if chave not in dados_agrupados:
            dados_agrupados[chave] = {
                'cr': cr,
                'contrato': contrato,
                'dias': {}
            }
        
        # Calcula porcentagem
        if total > 0:
            porcentagem = (finalizadas / total) * 100
        else:
            porcentagem = 0
        
        dados_agrupados[chave]['dias'][dia] = round(porcentagem, 1)
    
    # Converte para lista
    dados = list(dados_agrupados.values())
    
    cur.close()
    conn.close()
    
    return dados


def buscar_opcoes_filtros():
    """
    Retorna opções para os filtros (select)
    """
    conn = get_db_vista()
    cur = conn.cursor()
    
    # Busca valores únicos de cada campo
    filtros = {
        'clientes': [],
        'diretores_executivos': [],
        'diretores_regionais': [],
        'gerentes_regionais': [],
        'gerentes': [],
        'supervisores': [],
        'pec_01': [],
        'pec_02': []
    }
    
    # Clientes
    cur.execute("SELECT DISTINCT cliente FROM dw_vista.dm_estrutura WHERE cliente IS NOT NULL ORDER BY cliente")
    filtros['clientes'] = [row[0] for row in cur.fetchall()]
    
    # Gestores via dm_cr
    cur.execute("SELECT DISTINCT diretorexecutivo FROM dw_vista.dm_cr WHERE diretorexecutivo IS NOT NULL ORDER BY diretorexecutivo")
    filtros['diretores_executivos'] = [row[0] for row in cur.fetchall()]
    
    cur.execute("SELECT DISTINCT diretorregional FROM dw_vista.dm_cr WHERE diretorregional IS NOT NULL ORDER BY diretorregional")
    filtros['diretores_regionais'] = [row[0] for row in cur.fetchall()]
    
    cur.execute("SELECT DISTINCT gerenteregional FROM dw_vista.dm_cr WHERE gerenteregional IS NOT NULL ORDER BY gerenteregional")
    filtros['gerentes_regionais'] = [row[0] for row in cur.fetchall()]
    
    cur.execute("SELECT DISTINCT gerente FROM dw_vista.dm_cr WHERE gerente IS NOT NULL ORDER BY gerente")
    filtros['gerentes'] = [row[0] for row in cur.fetchall()]
    
    cur.execute("SELECT DISTINCT supervisor FROM dw_vista.dm_cr WHERE supervisor IS NOT NULL ORDER BY supervisor")
    filtros['supervisores'] = [row[0] for row in cur.fetchall()]
    
    # PECs
    cur.execute("SELECT DISTINCT nivel_01 FROM dw_vista.dm_estrutura WHERE nivel_01 IS NOT NULL ORDER BY nivel_01")
    filtros['pec_01'] = [row[0] for row in cur.fetchall()]
    
    cur.execute("SELECT DISTINCT nivel_02 FROM dw_vista.dm_estrutura WHERE nivel_02 IS NOT NULL ORDER BY nivel_02")
    filtros['pec_02'] = [row[0] for row in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return filtros

