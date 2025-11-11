from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.mensagem import (listar_mensagens, obter_mensagem, criar_mensagem,
                                 atualizar_mensagem, deletar_mensagem, toggle_ativa)
from app.models.grupo import listar_grupos

bp = Blueprint('mensagens', __name__, url_prefix='/mensagens')


@bp.route('/')
def lista():
    filtro_ativo = request.args.get('ativo', '')

    if filtro_ativo == 'true':
        mensagens = listar_mensagens(apenas_ativas=True)
    elif filtro_ativo == 'false':
        mensagens = listar_mensagens(apenas_ativas=False)
    else:
        mensagens = listar_mensagens()

    return render_template('mensagens/lista.html', mensagens=mensagens, filtro_ativo=filtro_ativo)


@bp.route('/nova')
def nova():
    grupos = listar_grupos()
    return render_template('mensagens/nova.html', grupos=grupos)


@bp.route('/criar', methods=['POST'])
def criar():
    try:
        grupos_ids = request.form.getlist('grupos')
        if 'todos' in grupos_ids:
            grupos_ids = ['TODOS']

        dias_semana = None
        if request.form['tipo_recorrencia'] == 'RECORRENTE':
            dias_semana = [int(d) for d in request.form.getlist('dias_semana')]

        dados = {
            'mensagem': request.form['mensagem'],
            'grupos_ids': grupos_ids,
            'tipo_recorrencia': request.form['tipo_recorrencia'],
            'dias_semana': dias_semana,
            'horario': request.form['horario'],
            'data_inicio': request.form['data_inicio'],
            'data_fim': request.form.get('data_fim') or None
        }

        mensagem_id = criar_mensagem(dados)
        flash(f'Mensagem criada com sucesso! ID: {mensagem_id}')
        return redirect(url_for('mensagens.lista'))

    except Exception as e:
        flash(f'Erro ao criar: {str(e)}')
        return redirect(url_for('mensagens.nova'))


@bp.route('/editar/<int:mensagem_id>')
def editar(mensagem_id):
    mensagem = obter_mensagem(mensagem_id)
    if not mensagem:
        flash('Mensagem não encontrada')
        return redirect(url_for('mensagens.lista'))

    grupos = listar_grupos()
    return render_template('mensagens/editar.html', mensagem=mensagem, grupos=grupos)


@bp.route('/atualizar/<int:mensagem_id>', methods=['POST'])
def atualizar(mensagem_id):
    try:
        grupos_ids = request.form.getlist('grupos')
        if 'todos' in grupos_ids:
            grupos_ids = ['TODOS']

        dias_semana = None
        if request.form['tipo_recorrencia'] == 'RECORRENTE':
            dias_semana = [int(d) for d in request.form.getlist('dias_semana')]

        dados = {
            'mensagem': request.form['mensagem'],
            'grupos_ids': grupos_ids,
            'tipo_recorrencia': request.form['tipo_recorrencia'],
            'dias_semana': dias_semana,
            'horario': request.form['horario'],
            'data_inicio': request.form['data_inicio'],
            'data_fim': request.form.get('data_fim') or None
        }

        atualizar_mensagem(mensagem_id, dados)
        flash('Mensagem atualizada!')
        return redirect(url_for('mensagens.lista'))

    except Exception as e:
        flash(f'Erro ao atualizar: {str(e)}')
        return redirect(url_for('mensagens.editar', mensagem_id=mensagem_id))


@bp.route('/toggle/<int:mensagem_id>', methods=['POST'])
def toggle(mensagem_id):
    try:
        novo_status = toggle_ativa(mensagem_id)
        return jsonify({'success': True, 'ativo': novo_status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@bp.route('/deletar/<int:mensagem_id>', methods=['POST'])
def deletar(mensagem_id):
    try:
        deletar_mensagem(mensagem_id)
        flash('Mensagem deletada!')
    except Exception as e:
        flash(f'Erro: {str(e)}')

    return redirect(url_for('mensagens.lista'))
