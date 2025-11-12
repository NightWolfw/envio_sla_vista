"""
Service para formatação de mensagens de agendamento SLA
"""
from datetime import datetime, timedelta


def obter_saudacao(hora_envio):
    """Retorna saudação baseada no horário de envio"""
    hora = hora_envio.hour

    if 5 <= hora < 12:
        return "Bom Dia"
    elif 12 <= hora < 18:
        return "Boa Tarde"
    else:
        return "Boa Noite"


def calcular_datas_consulta(data_envio, hora_inicio, offset_inicio, hora_fim, offset_fim):
    """
    Calcula datetime de início e fim da consulta baseado nos offsets

    Exemplo:
        data_envio: 2025-11-12 06:00:00 (segunda)
        hora_inicio: 23:00, offset: -1
        hora_fim: 05:00, offset: 0

        Retorna:
        - inicio: 2025-11-11 23:00:00 (domingo)
        - fim: 2025-11-12 05:00:00 (segunda)
    """
    data_base = data_envio.date()

    # Calcula data início
    data_inicio = datetime.combine(
        data_base + timedelta(days=offset_inicio),
        hora_inicio
    )

    # Calcula data fim
    data_fim = datetime.combine(
        data_base + timedelta(days=offset_fim),
        hora_fim
    )

    return data_inicio, data_fim


def calcular_emoji_sla(percentual):
    """Retorna emoji e texto baseado no percentual"""
    if percentual < 65:
        return "🔴", "ATENÇÃO – SLA BAIXO!"
    elif 65 <= percentual < 90:
        return "🟡", "SLA bom, mas podemos melhorar!"
    else:
        return "🟢", "EXCELENTE resultado pessoal, bom trabalho!"


def formatar_mensagem_resultados(data_inicio, data_fim, tarefas_stats, hora_envio):
    """Formata mensagem para Envio de Resultados"""
    saudacao = obter_saudacao(hora_envio)

    finalizadas = tarefas_stats['finalizadas']
    nao_realizadas = tarefas_stats['nao_realizadas']
    em_aberto = tarefas_stats['em_aberto']
    iniciadas = tarefas_stats['iniciadas']

    total = finalizadas + nao_realizadas + em_aberto + iniciadas
    percentual = (finalizadas / total * 100) if total > 0 else 0

    emoji, texto_sla = calcular_emoji_sla(percentual)

    mensagem = f"""{saudacao} pessoal, tudo bem?

Tarefas Realizadas no período de {data_inicio.strftime('%d/%m/%Y %H:%M')} até {data_fim.strftime('%d/%m/%Y %H:%M')}

✅ Tarefas finalizadas: {finalizadas}
❌ Tarefas não realizadas: {nao_realizadas}
📋 Tarefas em aberto: {em_aberto}
🔄 Tarefas iniciadas mas não finalizadas: {iniciadas}

📊 Porcentagem de tarefas realizadas: *{percentual:.1f}%*

{emoji} *{texto_sla}*

O detalhamento das tarefas será enviado abaixo para análise, grato pela colaboração de todos!"""

    return mensagem


def formatar_mensagem_programadas(data_inicio, data_fim, tarefas_stats, hora_envio):
    """Formata mensagem para Envio de Programadas"""
    saudacao = obter_saudacao(hora_envio)

    finalizadas = tarefas_stats['finalizadas']
    em_aberto = tarefas_stats['em_aberto']
    iniciadas = tarefas_stats['iniciadas']

    total_programadas = finalizadas + em_aberto

    mensagem = f"""{saudacao} pessoal, tudo bem?

Tarefas Programadas para o período de {data_inicio.strftime('%d/%m/%Y %H:%M')} até {data_fim.strftime('%d/%m/%Y %H:%M')}

✅ Tarefas finalizadas: {finalizadas}
📋 Tarefas em aberto: {em_aberto}
🔄 Tarefas iniciadas mas não finalizadas: {iniciadas}

📊 Total de tarefas programadas: *{total_programadas}*

O detalhamento das tarefas será enviado abaixo para análise, grato pela colaboração de todos!"""

    return mensagem
