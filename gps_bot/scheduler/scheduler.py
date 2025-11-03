from apscheduler.schedulers.blocking import BlockingScheduler
from database.gps_vista import GPSVistaDB
from services.message_formatter import MessageFormatter
from services.pdf_generator import PDFGenerator
from api.evolution import EvolutionAPI
from config import HORARIOS_ENVIO, EVOLUTION_CONFIG

scheduler = BlockingScheduler()

db = GPSVistaDB()
api = EvolutionAPI()

def tarefa_agendada(horario):
    print(f"Executando tarefa para horário {horario}...")

    # Obtenha os grupos para esse horário (implemente seu leitor de excel que filtra baseado no horário)
    from services.grupos_reader import GruposReader
    grupos_reader = GruposReader()
    grupos = grupos_reader.obter_grupos_filtrados(horario)

    for grupo in grupos:
        cr = grupo['CR']
        grupo_id = grupo['ID']

        # Buscar tarefas para CR com hora de consulta 5 minutos antes do horário
        tarefas = db.buscar_tarefas([cr], horario)

        # Separe tarefas realizadas, pendentes e não realizadas
        realizadas = [t for t in tarefas if t['Id_Status'] == 85]
        pendentes = [t for t in tarefas if t['Id_Status'] in [10, 25]]
        nao_realizadas = [t for t in tarefas if t['Id_Status'] not in [10, 25, 85]]

        # Formatar mensagem resumida
        mensagem = MessageFormatter.formatar_resumo(
            cr,
            total_realizadas=len(realizadas),
            total_pendentes=len(pendentes),
            total_nao_realizadas=len(nao_realizadas),
        )
        api.enviar_mensagem(grupo_id, mensagem)

        # Gerar e enviar PDF para pendentes e não realizadas (se existirem)
        if pendentes or nao_realizadas:
            pdf_path = f"relatorio_{cr}_{horario.replace(':', '')}.pdf"
            PDFGenerator.gerar_pdf_detalhes(pendentes, nao_realizadas, pdf_path)
            api.enviar_arquivo(grupo_id, pdf_path, legenda="Detalhamento das tarefas pendentes e não realizadas")

# Adiciona jobs para cada horário do config.py (hora e minuto)
for horario, _ in HORARIOS_ENVIO.items():
    hour, minute = map(int, horario.split(':'))
    # Agenda para rodar 5 minutos antes do horário para consulta
    scheduler.add_job(tarefa_agendada, 'cron', hour=hour, minute=minute - 5 if minute >= 5 else (60 + (minute - 5)), args=[horario])

if __name__ == "__main__":
    print("Iniciando scheduler...")
    scheduler.start()
