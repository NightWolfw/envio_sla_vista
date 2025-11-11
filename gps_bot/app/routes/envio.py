from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models.grupo import listar_grupos
from app.services.whatsapp import enviar_mensagem

bp = Blueprint('envio', __name__, url_prefix='/envio')


@bp.route('/')
def rapido():
    grupos = listar_grupos()
    return render_template('envio/rapido.html', grupos=grupos)


@bp.route('/processar', methods=['POST'])
def processar():
    try:
        mensagem = request.form['mensagem']
        grupos_ids = request.form.getlist('grupos')

        if not mensagem or not grupos_ids:
            return jsonify({'success': False, 'error': 'Preencha todos os campos'})

        # Busca grupos do banco
        from app.models.database import get_db_site
        conn = get_db_site()
        cur = conn.cursor()

        if 'todos' in grupos_ids:
            cur.execute("SELECT group_id, nome_grupo FROM grupos_whatsapp WHERE envio = true")
        else:
            placeholders = ','.join(['%s'] * len(grupos_ids))
            cur.execute(
                f"SELECT group_id, nome_grupo FROM grupos_whatsapp WHERE group_id IN ({placeholders}) AND envio = true",
                grupos_ids)

        grupos = cur.fetchall()
        cur.close()
        conn.close()

        if not grupos:
            return jsonify({'success': False, 'error': 'Nenhum grupo ativo selecionado'})

        # Envia mensagens
        sucessos = 0
        erros = 0
        detalhes = []

        for group_id, nome_grupo in grupos:
            sucesso, erro = enviar_mensagem(group_id, mensagem)

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
