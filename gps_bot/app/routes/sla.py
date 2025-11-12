from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from app.models.grupo import listar_grupos, buscar_crs_por_grupos
from app.models.sla import buscar_tarefas_para_sla, buscar_nome_contrato_por_cr
from app.services.scheduler import agendar_sla_pdf
from app.services.whatsapp import enviar_pdf_mensagem
from app.services.pdf_generator import gerar_pdf_sla

bp = Blueprint('sla', __name__, url_prefix='/sla')


@bp.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        try:
            grupos_ids = request.form.getlist('grupos[]')
            mensagem = request.form['mensagem']
            data_inicio = request.form['data_inicio']
            data_fim = request.form['data_fim']
            tipos_tarefa = request.form.getlist('tipos_tarefa')
            data_envio = request.form['data_envio']
            hora_envio = request.form['hora_envio']
            recorrencia = request.form['recorrencia']

            agendar_sla_pdf(grupos_ids, mensagem, data_inicio, data_fim, tipos_tarefa, data_envio, hora_envio,
                            recorrencia)
            flash('Agendamento criado com sucesso!')
            return redirect(url_for('sla.agendar'))
        except Exception as e:
            flash(f'Erro: {str(e)}')
            return redirect(url_for('sla.agendar'))

    grupos = listar_grupos()
    return render_template('sla/agendar.html', grupos=grupos)


@bp.route('/visualizar_pdf')
def visualizar_pdf():
    grupos_ids = request.args.getlist('grupos[]')
    mensagem = request.args.get('mensagem')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    tipos_tarefa = request.args.getlist('tipos_tarefa')

    # Debug - imprime no console
    print(f"DEBUG - Grupos IDs recebidos: {grupos_ids}")
    print(f"DEBUG - Data início: {data_inicio}, Data fim: {data_fim}")
    print(f"DEBUG - Tipos tarefa: {tipos_tarefa}")

    # BUSCA OS CRs A PARTIR DOS GROUP_IDs
    cr_list = buscar_crs_por_grupos(grupos_ids)
    print(f"DEBUG - CRs encontrados: {cr_list}")

    if not cr_list:
        return Response("Nenhum CR encontrado para os grupos selecionados", status=400)

    # Busca tarefas e verifica se inclui finalizadas
    tarefas, incluir_finalizadas = buscar_tarefas_para_sla(cr_list, data_inicio, data_fim, tipos_tarefa)
    print(f"DEBUG - Tarefas encontradas: {len(tarefas)}")
    print(f"DEBUG - Incluir finalizadas: {incluir_finalizadas}")

    # Busca o nome do contrato do primeiro CR
    contrato_nome = buscar_nome_contrato_por_cr(cr_list[0]) if len(cr_list) == 1 else "Multiplos Contratos"
    periodo_str = f"{data_inicio} a {data_fim}"

    # Gera PDF com flag de finalizadas
    pdf = gerar_pdf_sla(tarefas, cr_list[0], contrato_nome, periodo_str, incluir_finalizadas)

    return Response(pdf, mimetype='application/pdf')


@bp.route('/enviar_agora', methods=['POST'])
def enviar_agora():
    grupos_ids = request.form.getlist('grupos[]')
    mensagem = request.form['mensagem']
    data_inicio = request.form['data_inicio']
    data_fim = request.form['data_fim']
    tipos_tarefa = request.form.getlist('tipos_tarefa')

    # BUSCA OS CRs A PARTIR DOS GROUP_IDs
    cr_list = buscar_crs_por_grupos(grupos_ids)

    if not cr_list:
        return jsonify({'error': 'Nenhum CR encontrado para os grupos selecionados'}), 400

    # Busca tarefas
    tarefas, incluir_finalizadas = buscar_tarefas_para_sla(cr_list, data_inicio, data_fim, tipos_tarefa)

    # Busca nome do contrato
    contrato_nome = buscar_nome_contrato_por_cr(cr_list[0]) if len(cr_list) == 1 else "Multiplos Contratos"
    periodo_str = f"{data_inicio} a {data_fim}"

    # Gera PDF
    pdf = gerar_pdf_sla(tarefas, cr_list[0], contrato_nome, periodo_str, incluir_finalizadas)

    # Envia para os grupos via WhatsApp
    resultado = enviar_pdf_mensagem(grupos_ids, mensagem, pdf)

    return jsonify({'message': 'PDF enviado para os grupos!', 'resultado': resultado})
