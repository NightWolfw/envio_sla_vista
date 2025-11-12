from fpdf import FPDF


def gerar_pdf_sla(tarefas, cr, contrato_nome, periodo_str, incluir_finalizadas=False):
    """
    Gera PDF do SLA com colunas condicionais baseadas no tipo de tarefa
    Título mostra apenas o nivel_03 (nome do contrato)
    """
    pdf = FPDF(format='A4', orientation='L')  # Landscape para mais colunas
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título simplificado - apenas nivel_03
    titulo = f"Relatorio SLA - {contrato_nome}"
    pdf.cell(0, 10, titulo, ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Periodo: {periodo_str}", ln=True)
    pdf.ln(5)

    # Cabeçalho da tabela
    pdf.set_fill_color(200, 200, 200)
    pdf.set_font("Arial", style='B', size=9)

    if incluir_finalizadas:
        # Cabeçalho com colunas extras
        pdf.cell(20, 8, "CR", fill=1, border=1)
        pdf.cell(40, 8, "Contrato", fill=1, border=1)
        pdf.cell(35, 8, "Local", fill=1, border=1)
        pdf.cell(50, 8, "Tarefa", fill=1, border=1)
        pdf.cell(25, 8, "Disponib.", fill=1, border=1)
        pdf.cell(25, 8, "Prazo", fill=1, border=1)
        pdf.cell(25, 8, "Inicio Real", fill=1, border=1)
        pdf.cell(25, 8, "Termino Real", fill=1, border=1)
        pdf.cell(20, 8, "Expirada", ln=True, fill=1, border=1)
    else:
        # Cabeçalho padrão
        pdf.cell(25, 8, "CR", fill=1, border=1)
        pdf.cell(50, 8, "Contrato", fill=1, border=1)
        pdf.cell(45, 8, "Local", fill=1, border=1)
        pdf.cell(70, 8, "Tarefa", fill=1, border=1)
        pdf.cell(35, 8, "Disponibilizacao", fill=1, border=1)
        pdf.cell(30, 8, "Prazo", ln=True, fill=1, border=1)

    # Dados
    pdf.set_font("Arial", size=8)

    # Se não houver tarefas, adiciona mensagem
    if not tarefas or len(tarefas) == 0:
        pdf.cell(0, 10, "Nenhuma tarefa encontrada para o periodo selecionado", ln=True, align='C')

    for row in tarefas:
        if incluir_finalizadas:
            # 9 colunas
            pdf.cell(20, 7, str(row[0]), border=1)  # CR
            pdf.cell(40, 7, str(row[1])[:20], border=1)  # Contrato (truncado)
            pdf.cell(35, 7, str(row[2])[:15], border=1)  # Local
            pdf.cell(50, 7, str(row[3])[:25], border=1)  # Tarefa
            pdf.cell(25, 7, str(row[4])[:10], border=1)  # Disponibilização
            pdf.cell(25, 7, str(row[5]), border=1)  # Prazo
            pdf.cell(25, 7, str(row[6])[:10] if row[6] else '', border=1)  # Início Real
            pdf.cell(25, 7, str(row[7])[:10] if row[7] else '', border=1)  # Término Real
            pdf.cell(20, 7, str(row[8]) if row[8] else 'Nao', ln=True, border=1)  # Expirada
        else:
            # 6 colunas
            pdf.cell(25, 7, str(row[0]), border=1)  # CR
            pdf.cell(50, 7, str(row[1])[:25], border=1)  # Contrato
            pdf.cell(45, 7, str(row[2])[:20], border=1)  # Local
            pdf.cell(70, 7, str(row[3])[:35], border=1)  # Tarefa
            pdf.cell(35, 7, str(row[4])[:15], border=1)  # Disponibilização
            pdf.cell(30, 7, str(row[5]), ln=True, border=1)  # Prazo

    # Retorna bytes para o Flask
    return bytes(pdf.output(dest='S'))
