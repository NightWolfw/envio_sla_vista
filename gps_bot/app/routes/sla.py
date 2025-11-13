from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, send_file
from app.models.grupo import listar_grupos, obter_valores_unicos_filtros, buscar_crs_por_grupos, obter_grupo
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
from app.models.sla import buscar_tarefas_para_sla, buscar_nome_contrato_por_cr
from app.services.whatsapp import enviar_pdf_mensagem
from datetime import datetime, time

bp = Blueprint('sla', __name__, url_prefix='/sla')


@bp.route('/agendar', methods=['GET', 'POST'])
def agendar():
    """Página de agendamento de envios SLA - NOVA VERSÃO"""

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
    grupos = listar_grupos()
    filtros_disponiveis = obter_valores_unicos_filtros(apenas_ativos=True)

    return render_template(
        'agendamento/agendar.html',
        grupos=grupos,
        filtros=filtros_disponiveis
    )


@bp.route('/preview/<int:grupo_id>')
def preview_mensagem(grupo_id):
    """Retorna preview da mensagem para um grupo"""

    try:
        tipo_envio = request.args.get('tipo_envio', 'resultados')
        data_envio_str = request.args.get('data_envio')
        hora_inicio_str = request.args.get('hora_inicio')
        dia_offset_inicio = int(request.args.get('dia_offset_inicio', 0))
        hora_fim_str = request.args.get('hora_fim')
        dia_offset_fim = int(request.args.get('dia_offset_fim', 0))

        grupo = obter_grupo(grupo_id)

        if not grupo:
            return jsonify({'error': 'Grupo não encontrado'}), 404

        cr = grupo[4]
        nome_grupo = grupo[2]

        # Parse datetime
        data_envio = datetime.fromisoformat(data_envio_str)
        hora_inicio = time.fromisoformat(hora_inicio_str)
        hora_fim = time.fromisoformat(hora_fim_str)

        # Calcula período
        from datetime import timedelta
        data_inicio = data_envio + timedelta(days=dia_offset_inicio)
        data_inicio = datetime.combine(data_inicio.date(), hora_inicio)

        data_fim = data_envio + timedelta(days=dia_offset_fim)
        data_fim = datetime.combine(data_fim.date(), hora_fim)

        # BUSCA DADOS REAIS DO BANCO VISTA
        try:
            stats = buscar_tarefas_por_periodo(cr, data_inicio, data_fim, tipo_envio)
        except Exception as e:
            print(f"Erro ao buscar tarefas: {e}")
            # Se falhar, usa dados fictícios
            stats = {
                'finalizadas': 0,
                'nao_realizadas': 0,
                'em_aberto': 0,
                'iniciadas': 0
            }

        # Formata mensagem
        periodo = f"{data_inicio.strftime('%d/%m/%Y %H:%M')} até {data_fim.strftime('%d/%m/%Y %H:%M')}"

        if tipo_envio == 'resultados':
            mensagem = f"""📊 **Relatório de SLA - Resultados**

📅 Período: {periodo}
📤 Envio: {data_envio.strftime('%d/%m/%Y às %H:%M')}
🏢 Grupo: {nome_grupo}
🔢 CR: {cr}

✅ Finalizadas: {stats['finalizadas']}
❌ Não Realizadas: {stats['nao_realizadas']}
📝 Em Aberto: {stats['em_aberto']}
🔄 Iniciadas: {stats['iniciadas']}

📊 Total: {sum(stats.values())}
"""
        else:
            mensagem = f"""📋 **Relatório de SLA - Programadas**

📅 Período: {periodo}
📤 Envio: {data_envio.strftime('%d/%m/%Y às %H:%M')}
🏢 Grupo: {nome_grupo}
🔢 CR: {cr}

📝 Em Aberto: {stats['em_aberto']}
🔄 Iniciadas: {stats['iniciadas']}

📊 Total: {stats['em_aberto'] + stats['iniciadas']}
"""

        return jsonify({
            'mensagem': mensagem,
            'stats': stats,
            'grupo': nome_grupo,
            'cr': cr,
            'periodo': {
                'inicio': data_inicio.isoformat(),
                'fim': data_fim.isoformat()
            }
        })

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"ERRO NO PREVIEW: {error_detail}")
        return jsonify({'error': str(e), 'detail': error_detail}), 500


@bp.route('/gerar_pdf', methods=['POST'])
def gerar_pdf():
    """Gera PDF com relatório de tarefas"""

    try:
        dados = request.json

        grupo_id = dados['grupo_id']
        data_inicio = datetime.fromisoformat(dados['data_inicio'])
        data_fim = datetime.fromisoformat(dados['data_fim'])
        tipos_status = dados.get('tipos_status', ['finalizadas', 'em_aberto', 'iniciadas'])

        grupo = obter_grupo(grupo_id)

        cr = grupo[4]
        nome_grupo = grupo[2]

        tarefas = buscar_tarefas_detalhadas(cr, data_inicio, data_fim, tipos_status)

        caminho_pdf = gerar_pdf_relatorio(cr, nome_grupo, tarefas, data_inicio, data_fim, tipos_status)

        return send_file(caminho_pdf, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/listar')
def listar():
    """Lista agendamentos criados"""
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


# @bp.route('/visualizar_pdf')
# def visualizar_pdf():
#     """Rota antiga de visualizar PDF (DESABILITADA - usar a nova rota de agendamento)"""
#     # Esta rota foi desabilitada após migração para ReportLab
#     # Use as rotas /sla/agendar e /sla/download_pdf_agendamento
#     return jsonify({'error': 'Rota obsoleta. Use /sla/agendar'}), 410


# @bp.route('/enviar_agora', methods=['POST'])
# def enviar_agora():
#     """Rota antiga de enviar PDF (DESABILITADA - usar a nova rota de agendamento)"""
#     # Esta rota foi desabilitada após migração para ReportLab
#     # Use as rotas /sla/agendar para criar agendamentos
#     return jsonify({'error': 'Rota obsoleta. Use /sla/agendar'}), 410

@bp.route('/toggle/<int:agendamento_id>', methods=['POST'])
def toggle(agendamento_id):
    """Ativa/Desativa agendamento"""
    try:
        from app.models.agendamento import toggle_agendamento
        toggle_agendamento(agendamento_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@bp.route('/logs/<int:agendamento_id>')
def logs(agendamento_id):
    """Página de logs de um agendamento"""
    from app.models.agendamento import obter_logs_agendamento, obter_agendamento

    agendamento = obter_agendamento(agendamento_id)
    logs = obter_logs_agendamento(agendamento_id)

    return render_template('agendamento/logs.html', agendamento=agendamento, logs=logs)


@bp.route('/enviar_agora/<int:agendamento_id>', methods=['POST'])
def enviar_agora_manual(agendamento_id):
    """Executa envio manual de um agendamento"""
    try:
        from app.models.agendamento import obter_agendamento
        from app.services.scheduler_service import enviar_sla_agendado
        from app.models.grupo import obter_grupo

        # Busca agendamento
        agendamento_raw = obter_agendamento(agendamento_id)

        if not agendamento_raw:
            return jsonify({'success': False, 'error': 'Agendamento não encontrado'}), 404

        # Converte tupla para dict
        agendamento = {
            'id': agendamento_raw[0],
            'grupo_id': agendamento_raw[1],
            'tipo_envio': agendamento_raw[2],
            'dias_semana': agendamento_raw[3],
            'data_envio': agendamento_raw[4],
            'hora_inicio': agendamento_raw[5],
            'dia_offset_inicio': agendamento_raw[6],
            'hora_fim': agendamento_raw[7],
            'dia_offset_fim': agendamento_raw[8],
            'ativo': agendamento_raw[9]
        }

        # Busca grupo
        grupo = obter_grupo(agendamento['grupo_id'])

        # Executa envio
        enviar_sla_agendado(agendamento)

        return jsonify({
            'success': True,
            'message': f'Mensagem e PDF enviados para o grupo {grupo[2]}'
        })

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"ERRO NO ENVIO MANUAL: {error_detail}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_detail
        }), 500


@bp.route('/editar/<int:agendamento_id>')
def editar(agendamento_id):
    """Página de edição de agendamento"""
    from app.models.agendamento import obter_agendamento
    from app.models.grupo import listar_grupos, obter_valores_unicos_filtros

    agendamento = obter_agendamento(agendamento_id)

    if not agendamento:
        return "Agendamento não encontrado", 404

    filtros_valores = obter_valores_unicos_filtros(apenas_ativos=True)
    grupos = listar_grupos()
    grupos_ativos = [g for g in grupos if g[3]]

    return render_template('agendamento/editar.html',
                           agendamento=agendamento,
                           grupos=grupos_ativos,
                           filtros_valores=filtros_valores)


@bp.route('/atualizar/<int:agendamento_id>', methods=['POST'])
def atualizar(agendamento_id):
    """Atualiza um agendamento"""
    try:
        from app.models.agendamento import atualizar_agendamento

        dados = {
            'grupo_id': int(request.form['grupo_id']),
            'tipo_envio': request.form['tipo_envio'],
            'dias_semana': request.form['dias_semana'],
            'data_envio': request.form['data_envio'],
            'hora_inicio': request.form['hora_inicio'],
            'dia_offset_inicio': int(request.form['dia_offset_inicio']),
            'hora_fim': request.form['hora_fim'],
            'dia_offset_fim': int(request.form['dia_offset_fim'])
        }

        atualizar_agendamento(agendamento_id, dados)

        return jsonify({'success': True, 'message': 'Agendamento atualizado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
