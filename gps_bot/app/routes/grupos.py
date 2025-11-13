from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.grupo import listar_grupos, obter_valores_unicos_filtros, obter_grupo, atualizar_grupo
from app.services.whatsapp_sync import comparar_grupos_novos, inserir_grupos_novos
from app.services.estrutura import atualizar_dados_estrutura

bp = Blueprint('grupos', __name__, url_prefix='/grupos')


@bp.route('/')
@bp.route('/gerenciar')
def gerenciar():
    # Monta dicionário de filtros
    filtros = {}

    # ✅ Filtros básicos agora vão direto pro banco
    filtro_id = request.args.get('filtro_id', '')
    filtro_cr = request.args.get('filtro_cr', '')
    filtro_nome = request.args.get('filtro_nome', '')

    if filtro_id:
        filtros['id'] = filtro_id
    if filtro_cr:
        filtros['cr'] = filtro_cr
    if filtro_nome:
        filtros['nome'] = filtro_nome

    # Filtros de hierarquia
    if request.args.get('diretor_executivo'):
        filtros['diretorexecutivo'] = request.args.get('diretor_executivo')
    if request.args.get('diretor_regional'):
        filtros['diretorregional'] = request.args.get('diretor_regional')
    if request.args.get('gerente_regional'):
        filtros['gerenteregional'] = request.args.get('gerente_regional')
    if request.args.get('gerente'):
        filtros['gerente'] = request.args.get('gerente')
    if request.args.get('supervisor'):
        filtros['supervisor'] = request.args.get('supervisor')
    if request.args.get('cliente'):
        filtros['cliente'] = request.args.get('cliente')
    if request.args.get('pec_01'):
        filtros['pec_01'] = request.args.get('pec_01')
    if request.args.get('pec_02'):
        filtros['pec_02'] = request.args.get('pec_02')

    # ✅ Chama com dicionário ou None
    grupos = listar_grupos(filtros if filtros else None)

    # Pega valores únicos para os selects
    try:
        filtros_valores = obter_valores_unicos_filtros(apenas_ativos=False)
    except:
        filtros_valores = {}

    return render_template(
        'grupos/gerenciar.html',
        grupos=grupos,
        filtro_id=filtro_id,
        filtro_cr=filtro_cr,
        filtro_nome=filtro_nome,
        filtro_diretor_executivo=request.args.get('diretor_executivo', ''),
        filtro_diretor_regional=request.args.get('diretor_regional', ''),
        filtro_gerente_regional=request.args.get('gerente_regional', ''),
        filtro_gerente=request.args.get('gerente', ''),
        filtro_supervisor=request.args.get('supervisor', ''),
        filtro_cliente=request.args.get('cliente', ''),
        filtro_pec_01=request.args.get('pec_01', ''),
        filtro_pec_02=request.args.get('pec_02', ''),
        filtros_valores=filtros_valores
    )


@bp.route('/editar/<int:grupo_id>', methods=['GET', 'POST'])
def editar(grupo_id):
    """Edita um grupo específico"""
    if request.method == 'POST':
        dados = {
            'group_id': request.form.get('group_id'),
            'nome': request.form.get('nome'),
            'enviar_mensagem': request.form.get('enviar_mensagem') == 'on',
            'cr': request.form.get('cr')
        }

        try:
            atualizar_grupo(grupo_id, dados)
            flash('Grupo atualizado com sucesso!', 'success')
            return redirect(url_for('grupos.gerenciar'))
        except Exception as e:
            flash(f'Erro ao atualizar grupo: {str(e)}', 'error')

    # GET: Carrega dados do grupo
    grupo = obter_grupo(grupo_id)
    if not grupo:
        flash('Grupo não encontrado!', 'error')
        return redirect(url_for('grupos.gerenciar'))

    return render_template('grupos/editar.html', grupo=grupo)


@bp.route('/sincronizar-api', methods=['GET'])
def sincronizar_api():
    """Busca grupos novos da API"""
    try:
        grupos_novos = comparar_grupos_novos()
        return jsonify({
            'success': True,
            'grupos_novos': grupos_novos,
            'total': len(grupos_novos)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/adicionar-grupos-novos', methods=['POST'])
def adicionar_grupos_novos():
    """Adiciona grupos novos com CRs informados"""
    try:
        dados = request.get_json()
        grupos_com_cr = dados.get('grupos', [])
        
        resultado = inserir_grupos_novos(grupos_com_cr)
        
        return jsonify({
            'success': True,
            'inseridos': resultado['inseridos'],
            'estrutura_atualizada': resultado.get('estrutura_atualizada', 0),
            'erros': resultado['erros']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/sincronizar-estrutura', methods=['POST'])
def sincronizar_estrutura():
    """Sincroniza dados de estrutura (Cliente, PEC, Gestores) para todos os grupos com CR"""
    try:
        resultado = atualizar_dados_estrutura()
        return jsonify({
            'success': True,
            'total': resultado['total'],
            'atualizados': resultado['atualizados'],
            'erros': resultado['erros']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
