from flask import Blueprint, render_template, request, jsonify
from app.models.grupo import listar_grupos, obter_valores_unicos_filtros
from app.services.whatsapp import enviar_mensagem

bp = Blueprint('envio', __name__, url_prefix='/envio')

@bp.route('/')
def rapido():
    filtros_valores = obter_valores_unicos_filtros(apenas_ativos=True)
    grupos = listar_grupos()
    grupos_ativos = [g for g in grupos if g[3]]
    return render_template('envio/rapido.html', grupos=grupos_ativos, filtros_valores=filtros_valores)

@bp.route('/processar', methods=['POST'])
def processar():
    try:
        mensagem = request.form['mensagem']
        grupos_ids = request.form.getlist('grupos')
        if not mensagem or not grupos_ids:
            return jsonify({'success': False, 'error': 'Preencha todos os campos'})
        from app.models.database import get_db_site
        conn = get_db_site()
        cur = conn.cursor()
        placeholders = ','.join(['%s'] * len(grupos_ids))
        cur.execute(
            f"SELECT group_id, nome_grupo FROM grupos_whatsapp WHERE group_id IN ({placeholders}) AND envio = true",
            grupos_ids)
        grupos = cur.fetchall()
        cur.close()
        conn.close()
        if not grupos:
            return jsonify({'success': False, 'error': 'Nenhum grupo ativo selecionado'})
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
