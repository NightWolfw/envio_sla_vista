"""
Service para geração de PDF dos relatórios SLA
"""
from fpdf import FPDF
from datetime import datetime
import os


class PDFRelatorioSLA(FPDF):
    """Classe customizada para PDF de SLA"""

    def __init__(self, titulo, periodo_inicio, periodo_fim):
        super().__init__()
        self.titulo = titulo
        self.periodo_inicio = periodo_inicio
        self.periodo_fim = periodo_fim

    def header(self):
        """Cabeçalho do PDF"""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, self.titulo, 0, 1, 'C')

        self.set_font('Arial', '', 10)
        periodo = f"Período: {self.periodo_inicio.strftime('%d/%m/%Y %H:%M')} até {self.periodo_fim.strftime('%d/%m/%Y %H:%M')}"
        self.cell(0, 10, periodo, 0, 1, 'C')
        self.ln(5)

    def footer(self):
        """Rodapé do PDF"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')


def gerar_pdf_relatorio(cr, nome_grupo, tarefas, data_inicio, data_fim, tipos_status):
    """
    Gera PDF com relatório detalhado de tarefas

    Args:
        cr: Centro de Resultado
        nome_grupo: Nome do grupo WhatsApp
        tarefas: Lista de tarefas detalhadas
        data_inicio: datetime início período
        data_fim: datetime fim período
        tipos_status: tipos de status incluídos

    Returns:
        Caminho do arquivo PDF gerado
    """
    # Cria PDF
    titulo = f"Relatório SLA - CR {cr} - {nome_grupo}"
    pdf = PDFRelatorioSLA(titulo, data_inicio, data_fim)
    pdf.add_page()

    # Agrupa tarefas por status
    tarefas_por_status = {
        'Finalizada': [],
        'Não Realizada': [],
        'Em Aberto': [],
        'Iniciada': []
    }

    for tarefa in tarefas:
        status = tarefa['Status_Texto']
        if status in tarefas_por_status:
            tarefas_por_status[status].append(tarefa)

    # Renderiza cada grupo de status
    for status, lista_tarefas in tarefas_por_status.items():
        if not lista_tarefas:
            continue

        # Cabeçalho da seção
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f"{status} ({len(lista_tarefas)})", 0, 1)
        pdf.ln(2)

        # Tabela de tarefas
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(20, 7, 'ID', 1)
        pdf.cell(90, 7, 'Descrição', 1)
        pdf.cell(40, 7, 'Disponibilização', 1)
        pdf.cell(40, 7, 'Executor', 1)
        pdf.ln()

        pdf.set_font('Arial', '', 8)
        for tarefa in lista_tarefas:
            pdf.cell(20, 6, str(tarefa['Id_Tarefa']), 1)

            # Trunca descrição longa
            descricao = tarefa['Descricao'][:40] + '...' if len(tarefa['Descricao']) > 40 else tarefa['Descricao']
            pdf.cell(90, 6, descricao, 1)

            data_disp = tarefa['Disponibilizacao'].strftime('%d/%m/%Y %H:%M') if tarefa['Disponibilizacao'] else '-'
            pdf.cell(40, 6, data_disp, 1)

            executor = tarefa['Executor'] if tarefa['Executor'] else '-'
            pdf.cell(40, 6, executor[:20], 1)
            pdf.ln()

        pdf.ln(5)

    # Salva PDF
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f"relatorio_sla_{cr}_{timestamp}.pdf"
    caminho = os.path.join('app/static/uploads', nome_arquivo)

    pdf.output(caminho)

    return caminho
