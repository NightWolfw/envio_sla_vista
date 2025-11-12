from datetime import datetime, time
from app.models.mensagem import listar_mensagens
from app.models.grupo import listar_grupos
from app.models.log import registrar_envio
from app.services.whatsapp import enviar_mensagem, enviar_pdf_mensagem
from app.models.database import get_db_site
from app.models.sla import buscar_tarefas_para_sla
from app.services.pdf_generator import gerar_pdf_sla

def verificar_e_executar_envios():
    print(f"⏰ Verificando envios às {datetime.now().strftime('%H:%M:%S')}")
    agora = datetime.now()
    dia_semana_atual = agora.weekday()
    horario_atual = agora.strftime('%H:%M')
    data_atual = agora.date()
    mensagens = listar_mensagens(apenas_ativas=True)
    envios_realizados = 0
    for mensagem in mensagens:
        mensagem_id = mensagem[0]
        texto = mensagem[1]
        grupos_selecionados = mensagem[2]
        tipo_recorrencia = mensagem[3]
        dias_semana = mensagem[4]
        horario = mensagem[5]
        data_inicio = mensagem[6]
        data_fim = mensagem[7]
        if data_atual < data_inicio:
            continue
        if data_fim and data_atual > data_fim:
            continue
        if horario != horario_atual:
            continue
        if tipo_recorrencia == 'RECORRENTE':
            if not dias_semana or dia_semana_atual not in dias_semana:
                continue
        elif tipo_recorrencia == 'UNICO':
            if data_atual != data_inicio:
                continue
        print(f"📤 Enviando mensagem ID {mensagem_id}")
        grupos = obter_grupos_para_envio(grupos_selecionados)
        for group_id, nome_grupo in grupos:
            sucesso, erro = enviar_mensagem(group_id, texto)
            status = 'SUCESSO' if sucesso else 'ERRO'
            registrar_envio(mensagem_id, group_id, nome_grupo, texto, status, erro)
            envios_realizados += 1
    print(f"✅ Total de envios de mensagem realizados: {envios_realizados}")
    # Lógica para SLA PDF pode ser adicionada aqui

def obter_grupos_para_envio(grupos_selecionados):
    """Retorna lista de grupos que devem receber mensagem"""
    conn = get_db_site()
    cur = conn.cursor()
    if grupos_selecionados and grupos_selecionados[0] == 'TODOS':
        cur.execute("SELECT group_id, nome_grupo FROM grupos_whatsapp WHERE envio = true")
    else:
        placeholders = ','.join(['%s'] * len(grupos_selecionados))
        cur.execute(
            f"SELECT group_id, nome_grupo FROM grupos_whatsapp WHERE group_id IN ({placeholders}) AND envio = true",
            grupos_selecionados
        )
    grupos = cur.fetchall()
    cur.close()
    conn.close()
    return grupos

def enviar_mensagem_imediata(mensagem_id):
    """Envia mensagem agendada imediatamente, ignorando horário"""
    from app.models.mensagem import obter_mensagem
    mensagem = obter_mensagem(mensagem_id)
    if not mensagem:
        return {'sucesso': False, 'erro': 'Mensagem não encontrada'}
    texto = mensagem[1]
    grupos_selecionados = mensagem[2]
    grupos = obter_grupos_para_envio(grupos_selecionados)
    if not grupos:
        return {'sucesso': False, 'erro': 'Nenhum grupo disponível'}
    sucessos = 0
    erros = 0
    for group_id, nome_grupo in grupos:
        sucesso, erro = enviar_mensagem(group_id, texto)
        status = 'SUCESSO' if sucesso else 'ERRO'
        registrar_envio(mensagem_id, group_id, nome_grupo, texto, status, erro)
        if sucesso:
            sucessos += 1
        else:
            erros += 1
    return {
        'sucesso': True,
        'total_grupos': len(grupos),
        'sucessos': sucessos,
        'erros': erros
    }

def agendar_sla_pdf(grupos_ids, mensagem, data_inicio, data_fim, tipos_tarefa, data_envio, hora_envio, recorrencia):
    """
    Agenda o envio de SLA PDF para os grupos selecionados (recorrente ou único)
    """
    # Aqui você salva o agendamento, pode usar banco, scheduler, etc.
    pass
