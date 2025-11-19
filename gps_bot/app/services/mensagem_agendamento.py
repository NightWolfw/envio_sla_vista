from datetime import datetime, timedelta
import re
from typing import Any, Dict

import pytz

from app.models.sla_template import (
    DEFAULT_PROGRAMADAS_TEMPLATE,
    DEFAULT_RESULTADOS_TEMPLATE,
    get_sla_templates,
)

TIMEZONE_BRASILIA = pytz.timezone("America/Sao_Paulo")


def _to_brasilia(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return TIMEZONE_BRASILIA.localize(dt)
    return dt.astimezone(TIMEZONE_BRASILIA)


def calcular_datas_consulta(data_envio, hora_inicio, dia_offset_inicio, hora_fim, dia_offset_fim):
    """
    Calcula data_inicio e data_fim baseado nos offsets
    """
    base = _to_brasilia(data_envio)

    data_inicio = base + timedelta(days=dia_offset_inicio)
    inicio_naive = datetime.combine(data_inicio.date(), hora_inicio)
    data_inicio = TIMEZONE_BRASILIA.localize(inicio_naive)

    data_fim = base + timedelta(days=dia_offset_fim)
    fim_naive = datetime.combine(data_fim.date(), hora_fim)
    data_fim = TIMEZONE_BRASILIA.localize(fim_naive)

    return data_inicio, data_fim


def obter_saudacao():
    """Retorna saudacao baseada na hora atual"""
    hora = datetime.now(TIMEZONE_BRASILIA).hour

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


def _render_template(template: str, contexto: Dict[str, Any]) -> str:
    pattern = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")

    def replace(match: re.Match[str]) -> str:
        chave = match.group(1)
        valor = contexto.get(chave, "")
        return str(valor) if valor is not None else ""

    return pattern.sub(replace, template)


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

    contexto = {
        "saudacao": saudacao,
        "periodo_inicio": periodo_inicio,
        "periodo_fim": periodo_fim,
        "periodo_completo": f"{periodo_inicio} até {periodo_fim}",
        "finalizadas": finalizadas,
        "nao_realizadas": nao_realizadas,
        "em_aberto": em_aberto,
        "iniciadas": iniciadas,
        "total": total,
        "porcentagem": f"{porcentagem:.1f}",
        "emoji": emoji,
        "feedback": feedback,
        "data_envio": data_envio.strftime('%d/%m/%Y %H:%M'),
    }

    templates = get_sla_templates()
    template_texto = templates.get("resultados") or DEFAULT_RESULTADOS_TEMPLATE
    mensagem = _render_template(template_texto, contexto).strip()
    if not mensagem:
        mensagem = _render_template(DEFAULT_RESULTADOS_TEMPLATE, contexto)
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

    contexto = {
        "saudacao": saudacao,
        "periodo_inicio": data_inicio.strftime('%H:%M'),
        "periodo_fim": data_fim.strftime('%H:%M'),
        "periodo_completo": periodo_texto,
        "finalizadas": stats.get('finalizadas', 0),
        "nao_realizadas": stats.get('nao_realizadas', 0),
        "em_aberto": em_aberto,
        "iniciadas": iniciadas,
        "total_programadas": total_programadas,
        "emoji": "",
        "feedback": "",
        "porcentagem": "0.0",
        "data_envio": data_envio.strftime('%d/%m/%Y %H:%M'),
    }

    templates = get_sla_templates()
    template_texto = templates.get("programadas") or DEFAULT_PROGRAMADAS_TEMPLATE
    mensagem = _render_template(template_texto, contexto).strip()
    if not mensagem:
        mensagem = _render_template(DEFAULT_PROGRAMADAS_TEMPLATE, contexto)
    return mensagem
