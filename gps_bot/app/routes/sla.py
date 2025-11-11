from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.grupo import listar_grupos
from app.models.sla import buscar_tarefas_para_sla
from app.services.scheduler import agendar_sla_pdf
from app.services.whatsapp import enviar_pdf_mensagem

bp = Blueprint('sla', __name__, url_prefix='/sla')

@bp.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        try:
            grupos_ids = request.form.getlist('grupos')
            mensagem = request.form['mensagem']
            data_inicio = request.form['data_inicio']
            data_fim = request.form['data_fim']
            tipos_tarefa = request.form.getlist('tipos_tarefa')
            data_envio = request.form['data_envio']
            hora_envio = request.form['hora_envio']
            agendar_sla_pdf(grupos_ids, mensagem, data_inicio, data_fim, tipos_tarefa, data_envio, hora_envio)
            flash('Agendamento criado com sucesso!')
            return redirect(url_for('sla.agendar'))
        except Exception as e:
            flash(f'Erro: {str(e)}')
            return redirect(url_for('sla.agendar'))
    grupos = listar_grupos()
    return render_template('sla/agendar.html', grupos=grupos)
