# services/pdf_generator.py

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# Registrar fonte Calibri - ajuste para indicar o caminho correto no seu sistema se necessário
# Exemplo básico, talvez precise do arquivo .ttf local para Calibri, ou pode usar fonte similar padrão
try:
    pdfmetrics.registerFont(TTFont('Calibri', 'calibri.ttf'))
    fonte_tabela = 'Calibri'
except:
    fonte_tabela = 'Helvetica'  # fallback


class PDFGenerator:
    STATUS_LEGENDAS = {
        10: 'ABERTA',
        25: 'INICIADA',
        85: 'FINALIZADA'
    }

    @staticmethod
    def gerar_pdf_detalhes(tarefas_pendentes, tarefas_nao_realizadas, caminho_arquivo):
        doc = SimpleDocTemplate(
            caminho_arquivo,
            pagesize=letter,
            leftMargin=30,  # margem esquerda menor (padrão normalmente é 72)
            rightMargin=30  # margem direita menor
        )
        styles = getSampleStyleSheet()


        # Criar estilo para título e cabeçalho
        titulo_style = styles['Title']
        titulo_style.fontName = fonte_tabela

        elementos = []

        elementos.append(Paragraph("Relatório de Tarefas Pendentes e Não Realizadas", titulo_style))
        elementos.append(Spacer(1, 12))

        def construir_tabela(titulo, tarefas):
            if tarefas:
                h2_style = ParagraphStyle(name='Heading2Cal', parent=styles['Heading2'], fontName=fonte_tabela)
                elementos.append(Paragraph(titulo, h2_style))
                dados = [['Numero', 'Nome da Tarefa', 'Status', 'Prazo', 'Executor']]
                for t in tarefas:
                    status_code = int(t.get('Id_Status', 0))
                    status_text = PDFGenerator.STATUS_LEGENDAS.get(status_code, str(status_code))
                    dados.append([
                        t.get('Numero', ''),
                        t.get('Nome_Tarefa', ''),
                        status_text,
                        str(t.get('Prazo', '')),
                        t.get('Executor', '')
                    ])

                tabela = Table(dados, hAlign='LEFT', colWidths=[50, 200, 80, 80, 100])
                tabela.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#002443')),  # header azul escuro
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # texto branco no header
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), fonte_tabela),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ]))
                elementos.append(tabela)
                elementos.append(Spacer(1, 24))

        construir_tabela("Tarefas Pendentes", tarefas_pendentes)
        construir_tabela("Tarefas Não Realizadas", tarefas_nao_realizadas)

        doc.build(elementos)
