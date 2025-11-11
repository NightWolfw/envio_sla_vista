from fpdf import FPDF


def gerar_pdf_sla(tarefas, cr, contrato_nome, periodo_str):
    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    titulo = f"Envio Relatório SLA {cr} - {contrato_nome}"
    pdf.cell(0, 10, titulo, ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Período: {periodo_str}", ln=True)
    pdf.ln(5)
    pdf.set_fill_color(200,200,200)
    pdf.set_font("Arial", style='B', size=10)
    pdf.cell(50, 8, "Local", fill=1)
    pdf.cell(65, 8, "Nome da Tarefa", fill=1)
    pdf.cell(30, 8, "Disponibilização", fill=1)
    pdf.cell(25, 8, "Prazo", ln=True, fill=1)
    pdf.set_font("Arial", size=10)

    for row in tarefas:
        pdf.cell(50, 8, str(row[1]), border=0)
        pdf.cell(65, 8, str(row[2]), border=0)
        pdf.cell(30, 8, str(row[3]), border=0)
        pdf.cell(25, 8, str(row[4]), ln=True, border=0)

    return pdf.output(dest='S').encode('latin1')
