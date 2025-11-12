from datetime import datetime, timedelta


def calcular_datas_consulta(data_envio, hora_inicio, dia_offset_inicio, hora_fim, dia_offset_fim):
    """
    Calcula data_inicio e data_fim baseado nos offsets
    """
    data_inicio = data_envio + timedelta(days=dia_offset_inicio)
    data_inicio = datetime.combine(data_inicio.date(), hora_inicio)

    data_fim = data_envio + timedelta(days=dia_offset_fim)
    data_fim = datetime.combine(data_fim.date(), hora_fim)

    return data_inicio, data_fim


def obter_saudacao():
    """Retorna saudação baseada na hora atual"""
    hora = datetime.now().hour

    if 5 <= hora < 12:
        return "Bom Dia"
    elif 12 <= hora < 18:
        return "Boa Tarde"
    else:
        return "Boa Noite"


def calcular_porcentagem_feedback(finalizadas, total):
    """
    Calcula porcentagem e retorna emoji + mensagem de feedback
    """
    if total == 0:
        return 0, "⚪", ""

    porcentagem = (finalizadas / total) * 100

    if porcentagem < 65:
        emoji = "🔴"
        feedback = "*ATENÇÃO – SLA BAIXO!*"
    elif porcentagem < 90:
        emoji = "🟡"
        feedback = "*SLA bom, mas podemos melhorar!*"
    else:
        emoji = "🟢"
        feedback = "*EXCELENTE resultado pessoal, bom trabalho!*"

    return porcentagem, emoji, feedback


def formatar_mensagem_resultados(data_inicio, data_fim, stats, data_envio):
    """
    Formata mensagem de resultados de tarefas
    """
    saudacao = obter_saudacao()
    periodo_inicio = data_inicio.strftime('%H:%M')
    periodo_fim = data_fim.strftime('%H:%M')

    finalizadas = stats.get('finalizadas', 0)
    nao_realizadas = stats.get('nao_realizadas', 0)
    em_aberto = stats.get('em_aberto', 0)
    iniciadas = stats.get('iniciadas', 0)

    total = finalizadas + nao_realizadas + em_aberto + iniciadas
    porcentagem, emoji, feedback = calcular_porcentagem_feedback(finalizadas, total)

    mensagem = f"""{saudacao} pessoal, tudo bem?

Tarefas Realizadas no período de {periodo_inicio} até {periodo_fim}

✅ Tarefas finalizadas: {finalizadas}
❌ Tarefas não realizadas: {nao_realizadas}
📝 Tarefas em aberto: {em_aberto}
🔄 Tarefas iniciadas mas não finalizadas: {iniciadas}

{emoji} Porcentagem de tarefas realizadas/programadas: *{porcentagem:.1f}%*

{feedback}

O detalhamento das tarefas será enviado abaixo para análise, grato pela colaboração de todos!"""

    return mensagem


def formatar_mensagem_programadas(data_inicio, data_fim, stats, data_envio):
    """
    Formata mensagem de tarefas programadas
    """
    saudacao = obter_saudacao()

    # Formata período com data e hora
    periodo_texto = f"{data_inicio.strftime('%d/%m/%Y às %H:%M')} até {data_fim.strftime('%d/%m/%Y às %H:%M')}"

    em_aberto = stats.get('em_aberto', 0)
    iniciadas = stats.get('iniciadas', 0)

    total_programadas = em_aberto + iniciadas

    mensagem = f"""{saudacao} pessoal, tudo bem?

Tarefas Programadas para o período de {periodo_texto}

📝 Tarefas em aberto: {em_aberto}
🔄 Tarefas iniciadas mas não finalizadas: {iniciadas}

📊 Total de tarefas programadas: *{total_programadas}*

O detalhamento das tarefas será enviado abaixo para análise, grato pela colaboração de todos!"""

    return mensagem
