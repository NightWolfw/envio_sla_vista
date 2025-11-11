from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.grupo import listar_grupos, obter_grupo, atualizar_grupo, deletar_grupo, toggle_envio

bp = Blueprint('grupos', __name__, url_prefix='/grupos')


@bp.route('/')
def gerenciar():
    filtros = {
        'filtro_id': request.args.get('filtro_id', ''),
        'filtro_cr': request.args.get('filtro_cr', ''),
        'filtro_nome': request.args.get('filtro_nome', '')
    }

    grupos = listar_grupos(filtros)
    return render_template('grupos/gerenciar.html', grupos=grupos, **filtros)


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
