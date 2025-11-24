from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os
from pathlib import Path

import pytz
import config as project_config

TIMEZONE_BRASILIA = pytz.timezone("America/Sao_Paulo")
PDF_DIR = Path(project_config.PDF_STORAGE_DIR)


def _to_brasilia(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return TIMEZONE_BRASILIA.localize(dt)
    return dt.astimezone(TIMEZONE_BRASILIA)


def _format_datetime(dt: datetime, pattern: str = '%d/%m/%Y %H:%M') -> str:
    if not dt:
        return ''
    return _to_brasilia(dt).strftime(pattern)


def _escape_html(texto: str) -> str:
    """
    Escapa caracteres especiais usados pelo Paragraph para evitar quebra de markup.
    """
    if texto is None:
        return ''
    return (
        str(texto)
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
    )


def quebrar_texto(texto, max_length=40):
    """Quebra texto em múltiplas linhas"""
    if not texto or len(str(texto)) <= max_length:
        return str(texto)

    palavras = str(texto).split()
    linhas = []
    linha_atual = []

    for palavra in palavras:
        teste = ' '.join(linha_atual + [palavra])
        if len(teste) <= max_length:
            linha_atual.append(palavra)
        else:
            if linha_atual:
                linhas.append(' '.join(linha_atual))
            linha_atual = [palavra]

    if linha_atual:
        linhas.append(' '.join(linha_atual))

    return '\n'.join(linhas)


def formatar_local(local, max_length=80):
    """
    Formata o campo de local para quebrar linhas sem perder conteúdo.
    """
    texto = str(local or 'N/A').strip()
    if not texto:
        texto = 'N/A'
    return quebrar_texto(texto, max_length)


def gerar_pdf_relatorio(cr, nome_grupo, tarefas, data_inicio, data_fim, tipo_envio='resultados'):
    """
    Gera PDF HORIZONTAL com relatório de tarefas
    """
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(TIMEZONE_BRASILIA).strftime('%Y%m%d_%H%M%S')
    filename = f"sla_{cr}_{timestamp}.pdf"
    filepath = PDF_DIR / filename

    # Documento HORIZONTAL (landscape)
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=landscape(A4),
        topMargin=1 * cm,
        bottomMargin=1 * cm,
        leftMargin=0.7 * cm,
        rightMargin=0.7 * cm,
    )
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=8,
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.gray,
        spaceAfter=10,
        alignment=TA_CENTER
    )
    body_style = ParagraphStyle(
        'BodyTable',
        parent=styles['Normal'],
        fontSize=6,
        leading=7,
        alignment=TA_LEFT
    )
    local_style = ParagraphStyle(
        'LocalTable',
        parent=body_style,
        wordWrap='CJK'
    )

    # Título
    title = Paragraph(f"<b>Relatório SLA - {nome_grupo}</b>", title_style)
    elements.append(title)

    # Período
    periodo_texto = f"Período: {_format_datetime(data_inicio)} até {_format_datetime(data_fim)} | CR: {cr}"
    subtitle = Paragraph(periodo_texto, subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3 * cm))

    # Tabela de tarefas
    if tarefas:
        # Cabeçalho (mudei "Descrição" para "Nome" pra ficar mais claro)
        data = [['Nº', 'Nome', 'Disponib.', 'Prazo', 'Início Real', 'Término Real', 'Status', 'Executor', 'Local']]

        # Dados
        for tarefa in tarefas:
            numero = str(tarefa.get('numero', ''))
            # ✅ Agora 'descricao' contém o valor de t.nome
            descricao = Paragraph(_escape_html(quebrar_texto(tarefa.get('descricao', ''), 30)), body_style)
            disponibilizacao = _format_datetime(tarefa.get('disponibilizacao'), '%d/%m %H:%M')
            prazo = _format_datetime(tarefa.get('prazo'), '%d/%m %H:%M')
            inicioreal = _format_datetime(tarefa.get('inicioreal'), '%d/%m %H:%M') or '-'
            terminoreal = _format_datetime(tarefa.get('terminoreal'), '%d/%m %H:%M') or '-'
            status_texto = str(tarefa.get('status_texto', ''))
            executor = Paragraph(_escape_html(quebrar_texto(tarefa.get('executor', 'N/A') or 'N/A', 20)), body_style)
            local = Paragraph(_escape_html(formatar_local(tarefa.get('local', 'N/A'), 120)), local_style)

            data.append([
                numero,
                descricao,
                disponibilizacao,
                prazo,
                inicioreal,
                terminoreal,
                status_texto,
                executor,
                local
            ])

        # Larguras das colunas (ajustado para caber tudo)
        col_widths = [1.6 * cm, 5 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 3 * cm, 6.7 * cm]

        # Cria tabela
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

            # Corpo
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),

            # Ajustes de alinhamento por coluna
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Nº centralizado
            ('ALIGN', (8, 1), (8, -1), 'LEFT'),    # Local alinhado à esquerda
        ]))

        elements.append(table)
    else:
        no_data = Paragraph("<i>Nenhuma tarefa encontrada no período.</i>", styles['Normal'])
        elements.append(no_data)

    # Rodapé
    elements.append(Spacer(1, 0.5 * cm))
    footer = Paragraph(
        f"<i>Relatório gerado em {datetime.now(TIMEZONE_BRASILIA).strftime('%d/%m/%Y às %H:%M:%S')}</i>",
        subtitle_style
    )
    elements.append(footer)

    # Gera PDF
    doc.build(elements)

    return str(filepath)
