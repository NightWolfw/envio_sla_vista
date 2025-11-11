from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.grupo import (listar_grupos, obter_grupo, atualizar_grupo,
                              deletar_grupo, toggle_envio, obter_valores_unicos_filtros)

bp = Blueprint('grupos', __name__, url_prefix='/grupos')


@bp.route('/')
def gerenciar():
    # Busca valores únicos para dropdowns
    filtros_valores = obter_valores_unicos_filtros(apenas_ativos=False)

    # Captura filtros simples
    filtro_id = request.args.get('filtro_id', '')
    filtro_cr = request.args.get('filtro_cr', '')
    filtro_nome = request.args.get('filtro_nome', '')

    # Captura filtros avançados
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

    # Remove filtros vazios
    filtros = {k: v for k, v in filtros.items() if v}

    # Busca grupos com filtros
    grupos = listar_grupos(filtro_id, filtro_cr, filtro_nome, filtros if filtros else None)

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


@bp.route('/editar/<int:grupo_id>')
def editar(grupo_id):
    grupo = obter_grupo(grupo_id)
    if not grupo:
        flash('Grupo não encontrado')
        return redirect(url_for('grupos.gerenciar'))

    return render_template('grupos/editar.html', grupo=grupo)


@bp.route('/atualizar/<int:grupo_id>', methods=['POST'])
def atualizar(grupo_id):
    dados = {
        'group_id': request.form['group_id'],
        'nome_grupo': request.form['nome_grupo'],
        'envio': 'envio' in request.form,
        'dia_todo': 'dia_todo' in request.form,
        'cr': request.form['cr']
    }

    try:
        atualizar_grupo(grupo_id, dados)
        flash('Grupo atualizado!')
    except Exception as e:
        flash(f'Erro: {str(e)}')

    return redirect(url_for('grupos.gerenciar'))


@bp.route('/deletar/<int:grupo_id>', methods=['POST'])
def deletar(grupo_id):
    try:
        deletar_grupo(grupo_id)
        flash('Grupo deletado!')
    except Exception as e:
        flash(f'Erro: {str(e)}')

    return redirect(url_for('grupos.gerenciar'))


@bp.route('/toggle_envio/<int:grupo_id>', methods=['POST'])
def toggle(grupo_id):
    novo_status = toggle_envio(grupo_id)
    if novo_status is not None:
        return jsonify({'success': True, 'novo_status': novo_status})
    return jsonify({'success': False})
