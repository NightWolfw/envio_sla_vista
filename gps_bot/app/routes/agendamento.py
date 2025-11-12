"""
Rotas para agendamento de envio de SLA
"""
from flask import Blueprint, render_template, request, jsonify, send_file
from app.models.grupo import listar_grupos, obter_valores_unicos_filtros
from app.models.agendamento import (
    criar_agendamento, listar_agendamentos,
    obter_agendamento, deletar_agendamento
)
from app.services.mensagem_agendamento import (
    formatar_mensagem_resultados, formatar_mensagem_programadas,
    calcular_datas_consulta
)
from app.services.sla_consulta import buscar_tarefas_por_periodo, buscar_tarefas_detalhadas
from app.services.pdf_sla import gerar_pdf_relatorio
from datetime import datetime, time

bp = Blueprint('agendamento_sla', __name__, url_prefix='/sla-novo')


@bp.route('/agendar', methods=['GET', 'POST'])
def agendar():
    """Página de agendamento de envios SLA"""

    if request.method == 'POST':
        # Recebe dados do formulário
        dados = request.json

        try:
            # Cria agendamento para cada grupo selecionado
            grupos_ids = dados.get('grupos_ids', [])

            for grupo_id in grupos_ids:
                agendamento_data = {
                    'grupo_id': grupo_id,
                    'tipo_envio': dados['tipo_envio'],
                    'dias_semana': ','.join(dados['dias_semana']),
                    'data_envio': datetime.fromisoformat(dados['data_envio']),
                    'hora_inicio': time.fromisoformat(dados['hora_inicio']),
                    'dia_offset_inicio': int(dados['dia_offset_inicio']),
                    'hora_fim': time.fromisoformat(dados['hora_fim']),
                    'dia_offset_fim': int(dados['dia_offset_fim'])
                }

                criar_agendamento(agendamento_data)

            return jsonify({'success': True, 'message': 'Agendamentos criados com sucesso!'})

        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400

    # GET - Renderiza página
    # Busca apenas grupos ativos
    grupos = listar_grupos(filtros={'envio': True})
    filtros_disponiveis = obter_valores_unicos_filtros(apenas_ativos=True)

    return render_template(
        'agendamento/agendar.html',
        grupos=grupos,
        filtros=filtros_disponiveis
    )


@bp.route('/preview/<int:grupo_id>')
def preview_mensagem(grupo_id):
    """Retorna preview da mensagem para um grupo"""

    # Recebe parâmetros da query string
    tipo_envio = request.args.get('tipo_envio', 'resultados')
    data_envio = datetime.fromisoformat(request.args.get('data_envio'))
    hora_inicio = time.fromisoformat(request.args.get('hora_inicio'))
    dia_offset_inicio = int(request.args.get('dia_offset_inicio', 0))
    hora_fim = time.fromisoformat(request.args.get('hora_fim'))
    dia_offset_fim = int(request.args.get('dia_offset_fim', 0))

    # Busca grupo
    from app.models.grupo import obter_grupo
    grupo = obter_grupo(grupo_id)

    if not grupo:
        return jsonify({'error': 'Grupo não encontrado'}), 404

    cr = grupo[4]  # Assumindo posição do CR na tupla

    # Calcula datas de consulta
    data_inicio, data_fim = calcular_datas_consulta(
        data_envio, hora_inicio, dia_offset_inicio,
        hora_fim, dia_offset_fim
    )

    # Busca stats das tarefas
    stats = buscar_tarefas_por_periodo(cr, data_inicio, data_fim, tipo_envio)

    # Formata mensagem
    if tipo_envio == 'resultados':
        mensagem = formatar_mensagem_resultados(data_inicio, data_fim, stats, data_envio)
    else:
        mensagem = formatar_mensagem_programadas(data_inicio, data_fim, stats, data_envio)

    return jsonify({
        'mensagem': mensagem,
        'stats': stats,
        'periodo': {
            'inicio': data_inicio.isoformat(),
            'fim': data_fim.isoformat()
        }
    })


@bp.route('/gerar_pdf', methods=['POST'])
def gerar_pdf():
    """Gera PDF com relatório de tarefas"""

    dados = request.json

    grupo_id = dados['grupo_id']
    data_inicio = datetime.fromisoformat(dados['data_inicio'])
    data_fim = datetime.fromisoformat(dados['data_fim'])
    tipos_status = dados.get('tipos_status', ['finalizadas', 'em_aberto', 'iniciadas'])

    # Busca grupo
    from app.models.grupo import obter_grupo
    grupo = obter_grupo(grupo_id)

    cr = grupo[4]
    nome_grupo = grupo[2]

    # Busca tarefas detalhadas
    tarefas = buscar_tarefas_detalhadas(cr, data_inicio, data_fim, tipos_status)

    # Gera PDF
    caminho_pdf = gerar_pdf_relatorio(cr, nome_grupo, tarefas, data_inicio, data_fim, tipos_status)

    return send_file(caminho_pdf, as_attachment=True)


@bp.route('/listar')
def listar():
    """Lista agendamento criados"""
    agendamentos = listar_agendamentos()
    return render_template('agendamento/listar.html', agendamentos=agendamentos)


@bp.route('/deletar/<int:agendamento_id>', methods=['DELETE'])
def deletar(agendamento_id):
    """Deleta agendamento"""
    try:
        deletar_agendamento(agendamento_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400
