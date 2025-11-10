from flask import Flask, render_template, request, flash, redirect, url_for, send_file, jsonify
import pandas as pd
import psycopg2
import numpy as np
import os
from werkzeug.utils import secure_filename
from io import BytesIO
import sys

# Adiciona o diretório pai ao path para importar o config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def conectar_bd():
    """Conecta ao banco de dados do site admin (dw_sla)"""
    return psycopg2.connect(
        dbname=config.DB_SITE_CONFIG['database'],
        user=config.DB_SITE_CONFIG['user'],
        password=config.DB_SITE_CONFIG['password'],
        host=config.DB_SITE_CONFIG['host'],
        port=config.DB_SITE_CONFIG['port']
    )


def recriar_tabela():
    conn = conectar_bd()
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS grupos_whatsapp;")

    cur.execute("""
        CREATE TABLE grupos_whatsapp (
            id SERIAL PRIMARY KEY,
            group_id VARCHAR(255),
            nome_grupo VARCHAR(255),
            envio BOOLEAN,
            dia_todo BOOLEAN,
            cr VARCHAR(255)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


def importar_excel_para_bd(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo)
    conn = conectar_bd()
    cur = conn.cursor()

    for _, row in df.iterrows():
        dia_todo = None if pd.isna(row['DiaTodo']) else row['DiaTodo']

        if pd.isna(row['CR']):
            cr = None
        else:
            cr_valor = int(row['CR'])
            cr = f"{cr_valor:05d}"

        cur.execute("""
            INSERT INTO grupos_whatsapp (group_id, nome_grupo, envio, dia_todo, cr) 
            VALUES (%s, %s, %s, %s, %s)
        """, (row['ID'], row['Nome do Grupo'], row['Envio'], dia_todo, cr))

    conn.commit()
    cur.close()
    conn.close()


def exportar_bd_para_excel():
    conn = conectar_bd()
    df = pd.read_sql_query("""
        SELECT group_id as "ID", 
               nome_grupo as "Nome do Grupo", 
               envio as "Envio", 
               dia_todo as "DiaTodo", 
               cr as "CR" 
        FROM grupos_whatsapp 
        ORDER BY id
    """, conn)

    conn.close()

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')

    output.seek(0)
    return output


def buscar_grupos(filtro_id=None, filtro_cr=None, filtro_nome=None, filtros=None):
    conn = conectar_bd()
    cur = conn.cursor()

    query = """
        SELECT id, group_id, nome_grupo, envio, cr,
               cliente, pec_01, pec_02,
               diretorexecutivo, dia_todo
        FROM grupos_whatsapp 
        WHERE 1=1
    """
    params = []

    if filtro_id:
        query += " AND group_id ILIKE %s"
        params.append(f"%{filtro_id}%")

    if filtro_cr:
        query += " AND cr ILIKE %s"
        params.append(f"%{filtro_cr}%")

    if filtro_nome:
        query += " AND nome_grupo ILIKE %s"
        params.append(f"%{filtro_nome}%")

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

    query += " ORDER BY id"

    cur.execute(query, params)
    grupos = cur.fetchall()

    cur.close()
    conn.close()

    return grupos


def obter_grupo_por_id(grupo_id):
    conn = conectar_bd()
    cur = conn.cursor()

    cur.execute("SELECT * FROM grupos_whatsapp WHERE id = %s", (grupo_id,))
    grupo = cur.fetchone()

    cur.close()
    conn.close()

    return grupo


def atualizar_grupo(grupo_id, group_id, nome_grupo, envio, dia_todo, cr):
    conn = conectar_bd()
    cur = conn.cursor()

    cur.execute("""
        UPDATE grupos_whatsapp 
        SET group_id = %s, nome_grupo = %s, envio = %s, dia_todo = %s, cr = %s
        WHERE id = %s
    """, (group_id, nome_grupo, envio, dia_todo, cr, grupo_id))

    conn.commit()
    cur.close()
    conn.close()


def deletar_grupo(grupo_id):
    conn = conectar_bd()
    cur = conn.cursor()

    cur.execute("DELETE FROM grupos_whatsapp WHERE id = %s", (grupo_id,))

    conn.commit()
    cur.close()
    conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/gerenciar')
def gerenciar():
    filtros_valores = obter_valores_unicos_filtros(apenas_ativos=False)  # TODOS os grupos

    filtro_id = request.args.get('filtro_id', '')
    filtro_cr = request.args.get('filtro_cr', '')
    filtro_nome = request.args.get('filtro_nome', '')

    filtros = {
        'diretor_executivo': request.args.get('diretor_executivo', ''),
        'diretor_regional': request.args.get('diretor_regional', ''),
        'gerente_regional': request.args.get('gerente_regional', ''),
        'gerente': request.args.get('gerente', ''),
        'supervisor': request.args.get('supervisor', ''),
        'cliente': request.args.get('cliente', ''),
        'pec_01': request.args.get('pec_01', ''),
        'pec_02': request.args.get('pec_02', ''),
        'cr': filtro_cr
    }

    filtros = {k: v for k, v in filtros.items() if v}

    grupos = buscar_grupos(filtro_id, filtro_cr, filtro_nome, filtros if filtros else None)

    return render_template('gerenciar.html',
                           grupos=grupos,
                           filtro_id=filtro_id,
                           filtro_cr=filtro_cr,
                           filtro_nome=filtro_nome,
                           filtro_diretor_executivo=filtros.get('diretor_executivo', ''),
                           filtro_diretor_regional=filtros.get('diretor_regional', ''),
                           filtro_gerente_regional=filtros.get('gerente_regional', ''),
                           filtro_gerente=filtros.get('gerente', ''),
                           filtro_supervisor=filtros.get('supervisor', ''),
                           filtro_cliente=filtros.get('cliente', ''),
                           filtro_pec_01=filtros.get('pec_01', ''),
                           filtro_pec_02=filtros.get('pec_02', ''),
                           filtros_valores=filtros_valores)

@app.route('/editar/<int:grupo_id>')
def editar(grupo_id):
    grupo = obter_grupo_por_id(grupo_id)
    if not grupo:
        flash('Grupo não encontrado')
        return redirect(url_for('gerenciar'))

    return render_template('editar.html', grupo=grupo)


@app.route('/atualizar/<int:grupo_id>', methods=['POST'])
def atualizar(grupo_id):
    group_id = request.form['group_id']
    nome_grupo = request.form['nome_grupo']
    envio = 'envio' in request.form
    dia_todo = 'dia_todo' in request.form
    cr = request.form['cr']

    try:
        atualizar_grupo(grupo_id, group_id, nome_grupo, envio, dia_todo, cr)
        flash('Grupo atualizado com sucesso!')
    except Exception as e:
        flash(f'Erro ao atualizar: {str(e)}')

    return redirect(url_for('gerenciar'))


@app.route('/deletar/<int:grupo_id>', methods=['POST'])
def deletar(grupo_id):
    try:
        deletar_grupo(grupo_id)
        flash('Grupo deletado com sucesso!')
    except Exception as e:
        flash(f'Erro ao deletar: {str(e)}')

    return redirect(url_for('gerenciar'))


@app.route('/toggle_envio/<int:grupo_id>', methods=['POST'])
def toggle_envio(grupo_id):
    grupo = obter_grupo_por_id(grupo_id)
    if grupo:
        novo_envio = not grupo[3]  # grupo[3] é a coluna envio
        atualizar_grupo(grupo_id, grupo[1], grupo[2], novo_envio, grupo[4], grupo[5])
        return jsonify({'success': True, 'novo_status': novo_envio})

    return jsonify({'success': False})


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Nenhum arquivo foi enviado')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('Nenhum arquivo foi selecionado')
        return redirect(url_for('index'))

    if file and file.filename.endswith('.xlsx'):
        try:
            # Salva arquivo
            filepath = os.path.join('uploads', file.filename)
            file.save(filepath)

            # Importa com UPSERT (update ou insert)
            importar_excel_para_bd(filepath)

            flash('Planilha importada/atualizada com sucesso!')
        except Exception as e:
            flash(f'Erro ao importar: {str(e)}')

        return redirect(url_for('index'))
    else:
        flash('Por favor, envie um arquivo .xlsx')
        return redirect(url_for('index'))


@app.route('/export')
def export_file():
    try:
        output = exportar_bd_para_excel()
        return send_file(
            output,
            as_attachment=True,
            download_name='grupos_whatsapp_export.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        flash(f'Erro ao exportar: {str(e)}')
        return redirect(url_for('index'))


# ============================================
# FUNÇÕES PARA MÚLTIPLOS CRs
# ============================================

def adicionar_cr_ao_grupo(grupo_id, cr):
    """Adiciona um CR a um grupo"""
    conn = conectar_bd()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO grupo_cr (grupo_id, cr) VALUES (%s, %s)", (grupo_id, cr))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def remover_cr_do_grupo(grupo_id, cr):
    """Remove um CR de um grupo"""
    conn = conectar_bd()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM grupo_cr WHERE grupo_id = %s AND cr = %s", (grupo_id, cr))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def listar_crs_do_grupo(grupo_id):
    """Lista todos os CRs de um grupo (principal + adicionais)"""
    conn = conectar_bd()
    cur = conn.cursor()

    # Busca CR principal
    cur.execute("SELECT cr FROM grupos_whatsapp WHERE id = %s", (grupo_id,))
    resultado = cur.fetchone()
    cr_principal = resultado[0] if resultado else None

    # Busca CRs adicionais
    cur.execute("SELECT cr FROM grupo_cr WHERE grupo_id = %s ORDER BY cr", (grupo_id,))
    crs_adicionais = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    # Monta lista completa
    todos_crs = []
    if cr_principal:
        todos_crs.append(cr_principal)
    todos_crs.extend(crs_adicionais)

    return todos_crs


def limpar_crs_adicionais_grupo(grupo_id):
    """Remove todos os CRs adicionais de um grupo"""
    conn = conectar_bd()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM grupo_cr WHERE grupo_id = %s", (grupo_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


# ============================================
# FUNÇÕES PARA MENSAGENS AGENDADAS
# ============================================

def listar_todos_grupos(filtros=None, apenas_ativos=False):
    """Retorna lista de grupos com filtros opcionais"""
    conn = conectar_bd()
    cur = conn.cursor()

    query = """
        SELECT id, group_id, nome_grupo, envio, cr, 
               cliente, pec_01, pec_02,
               diretorexecutivo, diretorregional, 
               gerenteregional, gerente, supervisor
        FROM grupos_whatsapp 
        WHERE 1=1
    """
    params = []

    # Filtro invisível para mostrar apenas grupos com envio = true
    if apenas_ativos:
        query += " AND envio = true"

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

        if filtros.get('cr'):
            query += " AND cr LIKE %s"
            params.append(f"%{filtros['cr']}%")

    query += " ORDER BY nome_grupo"

    cur.execute(query, params)
    grupos = cur.fetchall()
    cur.close()
    conn.close()
    return grupos


def obter_valores_unicos_filtros():
    """Retorna valores únicos para os filtros dropdown (apenas grupos ativos)"""
    conn = conectar_bd()
    cur = conn.cursor()

    filtros = {}

    # Adiciona WHERE envio = true em todas as queries

    # Diretores Executivos
    cur.execute(
        "SELECT DISTINCT diretorexecutivo FROM grupos_whatsapp WHERE diretorexecutivo IS NOT NULL AND envio = true ORDER BY diretorexecutivo")
    filtros['diretor_executivo'] = [row[0] for row in cur.fetchall()]

    # Diretores Regionais
    cur.execute(
        "SELECT DISTINCT diretorregional FROM grupos_whatsapp WHERE diretorregional IS NOT NULL AND envio = true ORDER BY diretorregional")
    filtros['diretor_regional'] = [row[0] for row in cur.fetchall()]

    # Gerentes Regionais
    cur.execute(
        "SELECT DISTINCT gerenteregional FROM grupos_whatsapp WHERE gerenteregional IS NOT NULL AND envio = true ORDER BY gerenteregional")
    filtros['gerente_regional'] = [row[0] for row in cur.fetchall()]

    # Gerentes
    cur.execute(
        "SELECT DISTINCT gerente FROM grupos_whatsapp WHERE gerente IS NOT NULL AND envio = true ORDER BY gerente")
    filtros['gerente'] = [row[0] for row in cur.fetchall()]

    # Supervisores
    cur.execute(
        "SELECT DISTINCT supervisor FROM grupos_whatsapp WHERE supervisor IS NOT NULL AND envio = true ORDER BY supervisor")
    filtros['supervisor'] = [row[0] for row in cur.fetchall()]

    # Clientes
    cur.execute(
        "SELECT DISTINCT cliente FROM grupos_whatsapp WHERE cliente IS NOT NULL AND envio = true ORDER BY cliente")
    filtros['cliente'] = [row[0] for row in cur.fetchall()]

    # PEC 01
    cur.execute("SELECT DISTINCT pec_01 FROM grupos_whatsapp WHERE pec_01 IS NOT NULL AND envio = true ORDER BY pec_01")
    filtros['pec_01'] = [row[0] for row in cur.fetchall()]

    # PEC 02
    cur.execute("SELECT DISTINCT pec_02 FROM grupos_whatsapp WHERE pec_02 IS NOT NULL AND envio = true ORDER BY pec_02")
    filtros['pec_02'] = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()
    return filtros


def obter_valores_unicos_filtros(apenas_ativos=False):
    """Retorna valores únicos para os filtros dropdown"""
    conn = conectar_bd()
    cur = conn.cursor()

    filtros = {}

    # Adiciona filtro de envio = true apenas se especificado
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
    cur.execute(f"SELECT DISTINCT gerente FROM grupos_whatsapp {where_clause.format(campo='gerente')} ORDER BY gerente")
    filtros['gerente'] = [row[0] for row in cur.fetchall()]

    # Supervisores
    cur.execute(
        f"SELECT DISTINCT supervisor FROM grupos_whatsapp {where_clause.format(campo='supervisor')} ORDER BY supervisor")
    filtros['supervisor'] = [row[0] for row in cur.fetchall()]

    # Clientes
    cur.execute(f"SELECT DISTINCT cliente FROM grupos_whatsapp {where_clause.format(campo='cliente')} ORDER BY cliente")
    filtros['cliente'] = [row[0] for row in cur.fetchall()]

    # PEC 01
    cur.execute(f"SELECT DISTINCT pec_01 FROM grupos_whatsapp {where_clause.format(campo='pec_01')} ORDER BY pec_01")
    filtros['pec_01'] = [row[0] for row in cur.fetchall()]

    # PEC 02
    cur.execute(f"SELECT DISTINCT pec_02 FROM grupos_whatsapp {where_clause.format(campo='pec_02')} ORDER BY pec_02")
    filtros['pec_02'] = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()
    return filtros


def criar_mensagem_agendada(mensagem, grupos_ids, tipo_recorrencia, dias_semana, horario, data_inicio, data_fim=None):
    """Cria uma nova mensagem agendada"""
    conn = conectar_bd()
    cur = conn.cursor()

    # Se grupos_ids for 'TODOS', salva como array vazio (identificador especial)
    if grupos_ids == ['TODOS']:
        grupos_ids = ['TODOS']

    cur.execute("""
        INSERT INTO mensagens_agendadas 
        (mensagem, grupos_selecionados, tipo_recorrencia, dias_semana, horario, data_inicio, data_fim)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (mensagem, grupos_ids, tipo_recorrencia, dias_semana, horario, data_inicio, data_fim))

    mensagem_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return mensagem_id


def listar_mensagens_agendadas(apenas_ativas=None):
    """Lista mensagens agendadas com filtro opcional"""
    conn = conectar_bd()
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


def obter_mensagem_agendada(mensagem_id):
    """Busca uma mensagem agendada específica"""
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("SELECT * FROM mensagens_agendadas WHERE id = %s", (mensagem_id,))
    mensagem = cur.fetchone()
    cur.close()
    conn.close()
    return mensagem


def atualizar_mensagem_agendada(mensagem_id, mensagem, grupos_ids, tipo_recorrencia, dias_semana, horario, data_inicio,
                                data_fim=None):
    """Atualiza uma mensagem agendada existente"""
    conn = conectar_bd()
    cur = conn.cursor()

    if grupos_ids == ['TODOS']:
        grupos_ids = ['TODOS']

    cur.execute("""
        UPDATE mensagens_agendadas 
        SET mensagem = %s, 
            grupos_selecionados = %s, 
            tipo_recorrencia = %s, 
            dias_semana = %s, 
            horario = %s, 
            data_inicio = %s, 
            data_fim = %s,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (mensagem, grupos_ids, tipo_recorrencia, dias_semana, horario, data_inicio, data_fim, mensagem_id))

    conn.commit()
    cur.close()
    conn.close()


def toggle_mensagem_ativa(mensagem_id):
    """Ativa/Desativa uma mensagem agendada"""
    conn = conectar_bd()
    cur = conn.cursor()

    cur.execute("SELECT ativo FROM mensagens_agendadas WHERE id = %s", (mensagem_id,))
    ativo_atual = cur.fetchone()[0]
    novo_status = not ativo_atual

    cur.execute("UPDATE mensagens_agendadas SET ativo = %s WHERE id = %s", (novo_status, mensagem_id))

    conn.commit()
    cur.close()
    conn.close()
    return novo_status


def deletar_mensagem_agendada(mensagem_id):
    """Deleta uma mensagem agendada e seus logs"""
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("DELETE FROM mensagens_agendadas WHERE id = %s", (mensagem_id,))
    conn.commit()
    cur.close()
    conn.close()


def registrar_envio(mensagem_agendada_id, group_id, nome_grupo, mensagem, status, erro_detalhe=None):
    """Registra um envio no log"""
    conn = conectar_bd()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO log_envios 
        (mensagem_agendada_id, group_id, nome_grupo, mensagem, status, erro_detalhe)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (mensagem_agendada_id, group_id, nome_grupo, mensagem, status, erro_detalhe))

    conn.commit()
    cur.close()
    conn.close()


def listar_log_envios(mensagem_id=None, limit=100, offset=0):
    """Lista histórico de envios com paginação"""
    conn = conectar_bd()
    cur = conn.cursor()

    query = "SELECT * FROM log_envios WHERE 1=1"
    params = []

    if mensagem_id:
        query += " AND mensagem_agendada_id = %s"
        params.append(mensagem_id)

    query += " ORDER BY enviado_em DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cur.execute(query, params)
    logs = cur.fetchall()
    cur.close()
    conn.close()
    return logs


def obter_grupos_para_envio(mensagem_agendada):
    """Retorna lista de grupos que devem receber a mensagem"""
    grupos_selecionados = mensagem_agendada[2]  # índice da coluna grupos_selecionados

    conn = conectar_bd()
    cur = conn.cursor()

    if grupos_selecionados and grupos_selecionados[0] == 'TODOS':
        # Busca todos os grupos com envio = true
        cur.execute("SELECT group_id, nome_grupo FROM grupos_whatsapp WHERE envio = true")
    else:
        # Busca apenas os grupos selecionados
        placeholders = ','.join(['%s'] * len(grupos_selecionados))
        cur.execute(
            f"SELECT group_id, nome_grupo FROM grupos_whatsapp WHERE group_id IN ({placeholders}) AND envio = true",
            grupos_selecionados)

    grupos = cur.fetchall()
    cur.close()
    conn.close()
    return grupos


# ============================================
# ROTAS PARA MENSAGENS AGENDADAS
# ============================================

@app.route('/mensagens')
def mensagens():
    """Tela principal de mensagens agendadas"""
    filtro_ativo = request.args.get('ativo', '')

    if filtro_ativo == 'true':
        mensagens = listar_mensagens_agendadas(apenas_ativas=True)
    elif filtro_ativo == 'false':
        mensagens = listar_mensagens_agendadas(apenas_ativas=False)
    else:
        mensagens = listar_mensagens_agendadas()

    return render_template('mensagens.html', mensagens=mensagens, filtro_ativo=filtro_ativo)

@app.route('/mensagens/criar', methods=['POST'])
def criar_mensagem():
    """Processa criação de nova mensagem"""
    try:
        mensagem = request.form['mensagem']
        tipo_recorrencia = request.form['tipo_recorrencia']
        horario = request.form['horario']
        data_inicio = request.form['data_inicio']
        data_fim = request.form.get('data_fim') or None

        # Grupos selecionados
        grupos_ids = request.form.getlist('grupos')
        if 'todos' in grupos_ids:
            grupos_ids = ['TODOS']

        # Dias da semana (só para recorrente)
        dias_semana = None
        if tipo_recorrencia == 'RECORRENTE':
            dias_semana = [int(d) for d in request.form.getlist('dias_semana')]

        mensagem_id = criar_mensagem_agendada(
            mensagem, grupos_ids, tipo_recorrencia,
            dias_semana, horario, data_inicio, data_fim
        )

        flash(f'Mensagem agendada criada com sucesso! ID: {mensagem_id}')
        return redirect(url_for('mensagens'))

    except Exception as e:
        flash(f'Erro ao criar mensagem: {str(e)}')
        return redirect(url_for('nova_mensagem'))


@app.route('/mensagens/editar/<int:mensagem_id>')
def editar_mensagem(mensagem_id):
    """Tela para editar mensagem existente"""
    mensagem = obter_mensagem_agendada(mensagem_id)
    if not mensagem:
        flash('Mensagem não encontrada')
        return redirect(url_for('mensagens'))

    filtros_valores = obter_valores_unicos_filtros(apenas_ativos=True)  # Só grupos ativos
    grupos = listar_todos_grupos(apenas_ativos=True)
    return render_template('editar_mensagem.html', mensagem=mensagem, grupos=grupos, filtros_valores=filtros_valores)

@app.route('/mensagens/atualizar/<int:mensagem_id>', methods=['POST'])
def atualizar_mensagem(mensagem_id):
    """Processa atualização de mensagem"""
    try:
        mensagem = request.form['mensagem']
        tipo_recorrencia = request.form['tipo_recorrencia']
        horario = request.form['horario']
        data_inicio = request.form['data_inicio']
        data_fim = request.form.get('data_fim') or None

        grupos_ids = request.form.getlist('grupos')
        if 'todos' in grupos_ids:
            grupos_ids = ['TODOS']

        dias_semana = None
        if tipo_recorrencia == 'RECORRENTE':
            dias_semana = [int(d) for d in request.form.getlist('dias_semana')]

        atualizar_mensagem_agendada(
            mensagem_id, mensagem, grupos_ids, tipo_recorrencia,
            dias_semana, horario, data_inicio, data_fim
        )

        flash('Mensagem atualizada com sucesso!')
        return redirect(url_for('mensagens'))

    except Exception as e:
        flash(f'Erro ao atualizar mensagem: {str(e)}')
        return redirect(url_for('editar_mensagem', mensagem_id=mensagem_id))


@app.route('/mensagens/toggle/<int:mensagem_id>', methods=['POST'])
def toggle_mensagem(mensagem_id):
    """Ativa/Desativa mensagem via AJAX"""
    try:
        novo_status = toggle_mensagem_ativa(mensagem_id)
        return jsonify({'success': True, 'ativo': novo_status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/mensagens/deletar/<int:mensagem_id>', methods=['POST'])
def deletar_mensagem(mensagem_id):
    """Deleta mensagem agendada"""
    try:
        deletar_mensagem_agendada(mensagem_id)
        flash('Mensagem deletada com sucesso!')
    except Exception as e:
        flash(f'Erro ao deletar: {str(e)}')

    return redirect(url_for('mensagens'))


@app.route('/mensagens/historico')
def historico_envios():
    """Tela de histórico de envios"""
    mensagem_id = request.args.get('mensagem_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page

    logs = listar_log_envios(mensagem_id=mensagem_id, limit=per_page, offset=offset)

    return render_template('historico_envios.html',
                           logs=logs,
                           mensagem_id=mensagem_id,
                           page=page)

@app.route('/mensagens/detalhes/<int:mensagem_id>')
def detalhes_mensagem(mensagem_id):
    """Visualiza detalhes e logs de uma mensagem específica"""
    mensagem = obter_mensagem_agendada(mensagem_id)
    if not mensagem:
        flash('Mensagem não encontrada')
        return redirect(url_for('mensagens'))

    logs = listar_log_envios(mensagem_id=mensagem_id, limit=100)
    grupos = obter_grupos_para_envio(mensagem)

    return render_template('detalhes_mensagem.html',
                           mensagem=mensagem,
                           logs=logs,
                           grupos=grupos)


# ============================================
# FUNÇÃO PARA ENVIO IMEDIATO
# ============================================

def enviar_mensagem_whatsapp(group_id, mensagem):
    """Envia mensagem via Evolution API"""
    import requests

    url = f"{config.EVOLUTION_CONFIG['url']}/message/sendText/{config.EVOLUTION_CONFIG['instance']}"

    headers = {
        'Content-Type': 'application/json',
        'apikey': config.EVOLUTION_CONFIG['apikey']
    }

    payload = {
        'number': group_id,
        'text': mensagem
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True, None
    except Exception as e:
        return False, str(e)


@app.route('/mensagens/enviar-agora/<int:mensagem_id>', methods=['POST'])
def enviar_mensagem_agora(mensagem_id):
    """Envia mensagem imediatamente, ignorando agendamento"""
    print(f"🔥 CHAMOU ENVIAR AGORA - ID: {mensagem_id}")  # DEBUG
    try:
        mensagem = obter_mensagem_agendada(mensagem_id)
        if not mensagem:
            flash('Mensagem não encontrada')
            return redirect(url_for('mensagens'))

        mensagem_texto = mensagem[1]
        grupos_selecionados = mensagem[2]

        # Busca grupos para envio
        grupos = obter_grupos_para_envio(mensagem)

        if not grupos:
            flash('Nenhum grupo disponível para envio')
            return redirect(url_for('mensagens'))

        envios_sucesso = 0
        envios_erro = 0

        for group_id, nome_grupo in grupos:
            sucesso, erro = enviar_mensagem_whatsapp(group_id, mensagem_texto)

            if sucesso:
                registrar_envio(mensagem_id, group_id, nome_grupo, mensagem_texto, 'SUCESSO')
                envios_sucesso += 1
            else:
                registrar_envio(mensagem_id, group_id, nome_grupo, mensagem_texto, 'ERRO', erro)
                envios_erro += 1

        flash(f'Envio concluído! ✅ {envios_sucesso} sucesso | ❌ {envios_erro} erros')
        return redirect(url_for('detalhes_mensagem', mensagem_id=mensagem_id))

    except Exception as e:
        flash(f'Erro ao enviar: {str(e)}')
        return redirect(url_for('mensagens'))


@app.route('/envio-rapido')
def envio_rapido():
    """Página modal de envio rápido com filtros"""
    filtros_valores = obter_valores_unicos_filtros(apenas_ativos=True)  # Só grupos ativos

    filtros = {
        'diretor_executivo': request.args.get('diretor_executivo', ''),
        'diretor_regional': request.args.get('diretor_regional', ''),
        'gerente_regional': request.args.get('gerente_regional', ''),
        'gerente': request.args.get('gerente', ''),
        'supervisor': request.args.get('supervisor', ''),
        'cliente': request.args.get('cliente', ''),
        'pec_01': request.args.get('pec_01', ''),
        'pec_02': request.args.get('pec_02', ''),
        'cr': request.args.get('cr', '')
    }

    filtros = {k: v for k, v in filtros.items() if v}

    grupos = listar_todos_grupos(filtros if filtros else None, apenas_ativos=True)
    return render_template('envio_rapido.html', grupos=grupos, filtros=filtros, filtros_valores=filtros_valores)


@app.route('/mensagens/nova')
def nova_mensagem():
    """Tela para criar nova mensagem com filtros"""
    filtros_valores = obter_valores_unicos_filtros(apenas_ativos=True)  # Só grupos ativos

    filtros = {
        'diretor_executivo': request.args.get('diretor_executivo', ''),
        'diretor_regional': request.args.get('diretor_regional', ''),
        'gerente_regional': request.args.get('gerente_regional', ''),
        'gerente': request.args.get('gerente', ''),
        'supervisor': request.args.get('supervisor', ''),
        'cliente': request.args.get('cliente', ''),
        'pec_01': request.args.get('pec_01', ''),
        'pec_02': request.args.get('pec_02', ''),
        'cr': request.args.get('cr', '')
    }

    filtros = {k: v for k, v in filtros.items() if v}

    grupos = listar_todos_grupos(filtros if filtros else None, apenas_ativos=True)
    return render_template('nova_mensagem.html', grupos=grupos, filtros=filtros, filtros_valores=filtros_valores)

@app.route('/envio-rapido/enviar', methods=['POST'])
def processar_envio_rapido():
    """Processa envio rápido sem salvar agendamento"""
    try:
        mensagem = request.form['mensagem']
        grupos_ids = request.form.getlist('grupos')

        if not mensagem or not grupos_ids:
            return jsonify({'success': False, 'error': 'Preencha todos os campos'})

        # Busca grupos do banco
        conn = conectar_bd()
        cur = conn.cursor()

        if 'todos' in grupos_ids:
            # Se marcou "TODOS", considera apenas os grupos visíveis (filtrados)
            # Captura os IDs dos checkboxes individuais visíveis
            grupos_ids_visiveis = [gid for gid in grupos_ids if gid != 'todos']

            if not grupos_ids_visiveis:
                # Se não tem nenhum checkbox individual marcado, pega todos ativos
                cur.execute("SELECT group_id, nome_grupo FROM grupos_whatsapp WHERE envio = true")
            else:
                # Usa apenas os grupos visíveis (filtrados)
                placeholders = ','.join(['%s'] * len(grupos_ids_visiveis))
                cur.execute(
                    f"SELECT group_id, nome_grupo FROM grupos_whatsapp WHERE group_id IN ({placeholders}) AND envio = true",
                    grupos_ids_visiveis)
        else:
            # Envio para grupos selecionados manualmente
            placeholders = ','.join(['%s'] * len(grupos_ids))
            cur.execute(
                f"SELECT group_id, nome_grupo FROM grupos_whatsapp WHERE group_id IN ({placeholders}) AND envio = true",
                grupos_ids)

        grupos = cur.fetchall()
        cur.close()
        conn.close()

        if not grupos:
            return jsonify({'success': False, 'error': 'Nenhum grupo ativo selecionado'})

        # Envia para cada grupo
        sucessos = 0
        erros = 0
        detalhes = []

        for group_id, nome_grupo in grupos:
            sucesso, erro = enviar_mensagem_whatsapp(group_id, mensagem)

            if sucesso:
                sucessos += 1
                detalhes.append({'grupo': nome_grupo, 'status': 'SUCESSO'})
            else:
                erros += 1
                detalhes.append({'grupo': nome_grupo, 'status': 'ERRO', 'erro': erro})

        return jsonify({
            'success': True,
            'sucessos': sucessos,
            'erros': erros,
            'detalhes': detalhes
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def conectar_bd_vista():
    """Conecta ao banco de dados Vista (dw_gps)"""
    return psycopg2.connect(
        dbname=config.DB_CONFIG['database'],
        user=config.DB_CONFIG['user'],
        password=config.DB_CONFIG['password'],
        host=config.DB_CONFIG['host'],
        port=config.DB_CONFIG['port']
    )


def atualizar_dados_estrutura_multi_cr():
    """
    Atualiza dados de estrutura considerando múltiplos CRs por grupo
    """
    print("🔄 Iniciando atualização multi-CR...")

    conn_sla = conectar_bd()
    conn_vista = conectar_bd_vista()

    cur_sla = conn_sla.cursor()
    cur_vista = conn_vista.cursor()

    try:
        # Busca todos os grupos com seus CRs
        cur_sla.execute("""
            SELECT DISTINCT g.id, g.cr
            FROM grupos_whatsapp g
            WHERE g.cr IS NOT NULL AND g.cr != ''
        """)

        grupos_cr_principal = cur_sla.fetchall()

        total = len(grupos_cr_principal)
        atualizados = 0
        erros = 0

        print(f"📊 Total de grupos para atualizar: {total}")

        for grupo_id, cr_principal in grupos_cr_principal:
            try:
                # Busca todos os CRs do grupo (principal + adicionais)
                cur_sla.execute("""
                    SELECT cr FROM grupo_cr WHERE grupo_id = %s
                """, (grupo_id,))
                crs_adicionais = [row[0] for row in cur_sla.fetchall()]

                todos_crs = [cr_principal] + crs_adicionais
                todos_crs = [cr for cr in todos_crs if cr]  # Remove None/vazios

                print(f"🔍 Grupo {grupo_id}: Buscando CRs {todos_crs}")

                # Tenta buscar dados de cada CR até encontrar
                for cr in todos_crs:
                    cr_com_zeros = cr
                    cr_sem_zeros = cr.lstrip('0') if cr else None

                    if not cr_sem_zeros:
                        cr_sem_zeros = '0'

                    # Busca dados da estrutura
                    cur_vista.execute("""
                        SELECT 
                            cliente,
                            nivel_01 as pec_01,
                            nivel_02 as pec_02,
                            id_cr
                        FROM dw_vista.dm_estrutura
                        WHERE crno::text = %s OR crno::text = %s
                        LIMIT 1
                    """, (cr_com_zeros, cr_sem_zeros))

                    estrutura = cur_vista.fetchone()

                    if estrutura:
                        cliente, pec_01, pec_02, id_cr = estrutura

                        # Busca dados de gestores
                        cur_vista.execute("""
                            SELECT 
                                diretorexecutivo,
                                diretorregional,
                                gerenteregional,
                                gerente,
                                supervisor
                            FROM dw_vista.dm_cr
                            WHERE id_cr = %s
                            LIMIT 1
                        """, (id_cr,))

                        gestores = cur_vista.fetchone()

                        if gestores:
                            diretor_exec, diretor_reg, gerente_reg, gerente, supervisor = gestores

                            # Atualiza no banco SLA
                            cur_sla.execute("""
                                UPDATE grupos_whatsapp
                                SET cliente = %s,
                                    pec_01 = %s,
                                    pec_02 = %s,
                                    diretorexecutivo = %s,
                                    diretorregional = %s,
                                    gerenteregional = %s,
                                    gerente = %s,
                                    supervisor = %s,
                                    ultima_atualizacao = CURRENT_TIMESTAMP
                                WHERE id = %s
                            """, (cliente, pec_01, pec_02, diretor_exec, diretor_reg,
                                  gerente_reg, gerente, supervisor, grupo_id))

                            atualizados += 1
                            print(f"  ✅ Grupo {grupo_id} atualizado com CR {cr}")
                            print(f"     Cliente: {cliente} | PEC: {pec_01}/{pec_02}")
                            break  # Encontrou dados, para de buscar
                        else:
                            print(f"  ⚠️ Gestores não encontrados para CR {cr} (id_cr: {id_cr})")
                    else:
                        print(f"  ⚠️ Estrutura não encontrada para CR {cr}")

            except Exception as e:
                erros += 1
                print(f"  ❌ Erro ao processar grupo {grupo_id}: {str(e)}")

        conn_sla.commit()

        print(f"\n{'=' * 60}")
        print(f"✅ Atualização multi-CR concluída!")
        print(f"   Total: {total} | Atualizados: {atualizados} | Erros: {erros}")
        print(f"{'=' * 60}\n")

    except Exception as e:
        conn_sla.rollback()
        print(f"❌ Erro na atualização: {str(e)}")
        raise
    finally:
        cur_sla.close()
        cur_vista.close()
        conn_sla.close()
        conn_vista.close()


# Alias para manter compatibilidade
def atualizar_dados_estrutura():
    """Wrapper para manter compatibilidade com código existente"""
    return atualizar_dados_estrutura_multi_cr()


def importar_excel_para_bd(caminho_arquivo):
    """Importa dados do Excel com suporte a múltiplos CRs (UPSERT com tratamento de erro por linha)"""
    df = pd.read_excel(caminho_arquivo)
    conn = conectar_bd()

    grupos_novos = 0
    grupos_atualizados = 0
    crs_adicionais_total = 0
    erros = 0

    print(f"📥 Iniciando importação de {len(df)} linhas...")

    for index, row in df.iterrows():
        cur = conn.cursor()

        try:
            # Converte DiaTodo para boolean
            dia_todo = None if pd.isna(row['DiaTodo']) else bool(row['DiaTodo'])

            # Converte Envio para boolean (aceita 0/1, True/False, "TRUE"/"FALSE")
            if pd.isna(row['Envio']):
                envio = False
            else:
                envio_valor = row['Envio']
                if isinstance(envio_valor, (int, float)):
                    envio = bool(int(envio_valor))
                elif isinstance(envio_valor, str):
                    envio = envio_valor.upper() in ['TRUE', '1', 'SIM', 'YES']
                else:
                    envio = bool(envio_valor)

            # Processa múltiplos CRs separados por vírgula
            if pd.isna(row['CR']):
                cr_principal = None
                crs_adicionais = []
            else:
                cr_str = str(row['CR']).strip()

                # Se tem vírgula, separa múltiplos CRs
                if ',' in cr_str:
                    crs = [c.strip() for c in cr_str.split(',') if c.strip()]
                    # Formata com zeros à esquerda
                    crs_formatados = []
                    for c in crs:
                        try:
                            crs_formatados.append(f"{int(float(c)):05d}")  # float() pra aceitar "123.0"
                        except:
                            crs_formatados.append(c)

                    cr_principal = crs_formatados[0] if crs_formatados else None
                    crs_adicionais = crs_formatados[1:] if len(crs_formatados) > 1 else []
                else:
                    # CR único
                    try:
                        cr_principal = f"{int(float(cr_str)):05d}"
                    except:
                        cr_principal = cr_str
                    crs_adicionais = []

            # Verifica se grupo já existe (UPSERT)
            cur.execute("SELECT id FROM grupos_whatsapp WHERE group_id = %s", (row['ID'],))
            grupo_existente = cur.fetchone()

            if grupo_existente:
                grupo_id = grupo_existente[0]
                # UPDATE: Atualiza grupo existente
                cur.execute("""
                    UPDATE grupos_whatsapp 
                    SET nome_grupo = %s, 
                        envio = %s, 
                        dia_todo = %s, 
                        cr = %s
                    WHERE id = %s
                """, (row['Nome do Grupo'], envio, dia_todo, cr_principal, grupo_id))
                grupos_atualizados += 1

                # Limpa CRs adicionais antigos desse grupo
                cur.execute("DELETE FROM grupo_cr WHERE grupo_id = %s", (grupo_id,))
            else:
                # INSERT: Novo grupo
                cur.execute("""
                    INSERT INTO grupos_whatsapp (group_id, nome_grupo, envio, dia_todo, cr) 
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (row['ID'], row['Nome do Grupo'], envio, dia_todo, cr_principal))

                grupo_id = cur.fetchone()[0]
                grupos_novos += 1

            # Adiciona CRs secundários na tabela grupo_cr
            for cr_adicional in crs_adicionais:
                cur.execute("""
                    INSERT INTO grupo_cr (grupo_id, cr) 
                    VALUES (%s, %s)
                """, (grupo_id, cr_adicional))
                crs_adicionais_total += 1

            # Commit individual por linha
            conn.commit()
            cur.close()

            if (index + 1) % 50 == 0:
                print(f"  ✅ Processadas {index + 1}/{len(df)} linhas...")

        except Exception as e:
            # Rollback apenas dessa linha
            conn.rollback()
            cur.close()
            erros += 1
            print(f"  ❌ Erro na linha {index + 1} ({row.get('Nome do Grupo', 'N/A')}): {str(e)[:150]}")
            continue

    conn.close()

    print(f"\n{'=' * 60}")
    print(f"✅ Importação concluída!")
    print(f"   Grupos novos: {grupos_novos}")
    print(f"   Grupos atualizados: {grupos_atualizados}")
    print(f"   CRs adicionais: {crs_adicionais_total}")
    print(f"   Erros: {erros}")
    print(f"{'=' * 60}\n")

    # Atualiza dados da estrutura após importar
    if grupos_novos + grupos_atualizados > 0:
        print("📊 Atualizando dados da estrutura organizacional...")
        try:
            atualizar_dados_estrutura_multi_cr()
        except Exception as e:
            print(f"⚠️ Erro na atualização de estrutura: {e}")


@app.route('/atualizar-estrutura', methods=['POST'])
def trigger_atualizar_estrutura():
    """Rota para atualizar manualmente os dados da estrutura"""
    try:
        atualizar_dados_estrutura_multi_cr()
        flash('Dados da estrutura atualizados com sucesso!')
    except Exception as e:
        flash(f'Erro ao atualizar estrutura: {str(e)}')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
