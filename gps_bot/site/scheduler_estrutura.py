import time
import schedule
from datetime import datetime
import sys
import os
from app import atualizar_dados_estrutura_multi_cr

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa a função de atualização do app
from app import atualizar_dados_estrutura


def job_atualizar_estrutura():
    """Job que roda todos os dias às 23:59"""
    print(f"\n{'=' * 60}")
    print(f"⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Executando atualização agendada")
    print(f"{'=' * 60}\n")

    try:
        atualizar_dados_estrutura_multi_cr()
    except Exception as e:
        print(f"❌ Erro na atualização agendada: {e}")


# Agenda para rodar todos os dias às 23:59
schedule.every().day.at("23:59").do(job_atualizar_estrutura)

print("🚀 Scheduler de atualização de estrutura iniciado!")
print("📅 Agendado para rodar diariamente às 23:59")
print("Aguardando próxima execução...\n")

while True:
    schedule.run_pending()
    time.sleep(60)  # Verifica a cada minuto
