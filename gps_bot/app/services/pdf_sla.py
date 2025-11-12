from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os


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


def alinhar_direita_local(local, max_length=30):
    """
    Alinha local da direita pra esquerda
    Se ultrapassar o tamanho, mostra só a parte final
    """
    local_str = str(local) if local else ''

    if len(local_str) <= max_length:
        return local_str

    # Pega os últimos caracteres (direita)
    return '...' + local_str[-(max_length-3):]


def gerar_pdf_relatorio(cr, nome_grupo, tarefas, data_inicio, data_fim, tipo_envio='resultados'):
    """
    Gera PDF HORIZONTAL com relatório de tarefas
    """
    # Cria diretório
    temp_dir = 'temp_pdfs'
    os.makedirs(temp_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"sla_{cr}_{timestamp}.pdf"
    filepath = os.path.join(temp_dir, filename)

    # Documento HORIZONTAL (landscape)
    doc = SimpleDocTemplate(filepath, pagesize=landscape(A4), topMargin=1 * cm, bottomMargin=1 * cm)
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

    # Título
    title = Paragraph(f"<b>Relatório SLA - {nome_grupo}</b>", title_style)
    elements.append(title)

    # Período
    periodo_texto = f"Período: {data_inicio.strftime('%d/%m/%Y %H:%M')} até {data_fim.strftime('%d/%m/%Y %H:%M')} | CR: {cr}"
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
            descricao = quebrar_texto(tarefa.get('descricao', ''), 25)
            disponibilizacao = tarefa.get('disponibilizacao').strftime('%d/%m %H:%M') if tarefa.get(
                'disponibilizacao') else ''
            prazo = tarefa.get('prazo').strftime('%d/%m %H:%M') if tarefa.get('prazo') else ''
            inicioreal = tarefa.get('inicioreal').strftime('%d/%m %H:%M') if tarefa.get('inicioreal') else '-'
            terminoreal = tarefa.get('terminoreal').strftime('%d/%m %H:%M') if tarefa.get('terminoreal') else '-'
            status_texto = str(tarefa.get('status_texto', ''))
            executor = quebrar_texto(tarefa.get('executor', 'N/A') or 'N/A', 15)
            local = alinhar_direita_local(tarefa.get('local', 'N/A'), 25)

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
        col_widths = [1.2 * cm, 5 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm, 3 * cm, 5 * cm]

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

            # Local alinhado à direita
            ('ALIGN', (8, 1), (8, -1), 'RIGHT'),
        ]))

        elements.append(table)
    else:
        no_data = Paragraph("<i>Nenhuma tarefa encontrada no período.</i>", styles['Normal'])
        elements.append(no_data)

    # Rodapé
    elements.append(Spacer(1, 0.5 * cm))
    footer = Paragraph(
        f"<i>Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</i>",
        subtitle_style
    )
    elements.append(footer)

    # Gera PDF
    doc.build(elements)

    return filepath
