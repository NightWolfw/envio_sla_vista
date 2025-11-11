import requests
from config import EVOLUTION_CONFIG
from app.models.sla import buscar_tarefas_para_sla
from app.services.pdf_generator import gerar_pdf_sla


def enviar_mensagem(group_id, mensagem):
    """Envia mensagem via Evolution API"""
    url = f"{EVOLUTION_CONFIG['url']}/message/sendText/{EVOLUTION_CONFIG['instance']}"

    headers = {
        'Content-Type': 'application/json',
        'apikey': EVOLUTION_CONFIG['apikey']
    }

    payload = {
        'number': group_id,
        'text': mensagem
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True, None
    except Exception as e:
        return False, str(e)


def enviar_pdf_mensagem(grupo_id, mensagem, cr_list, data_inicio, data_fim, tipos_tarefa):
    """Envia PDF do SLA via Evolution API"""
    for cr in cr_list:
        tarefas = buscar_tarefas_para_sla([cr], data_inicio, data_fim, tipos_tarefa)
        if tarefas:
            contrato_nome = tarefas[0][0]
            periodo_str = f"{data_inicio} até {data_fim}"
            pdf_bytes = gerar_pdf_sla(tarefas, cr, contrato_nome, periodo_str)

            # Envia PDF via Evolution API
            url = f"{EVOLUTION_CONFIG['url']}/message/sendMedia/{EVOLUTION_CONFIG['instance']}"
            headers = {
                'apikey': EVOLUTION_CONFIG['apikey']
            }

            files = {
                'number': (None, grupo_id),
                'caption': (None, mensagem),
                'media': ('sla.pdf', pdf_bytes, 'application/pdf')
            }

            try:
                response = requests.post(url, headers=headers, files=files, timeout=30)
                response.raise_for_status()
                print(f"✅ PDF enviado para grupo {grupo_id}, CR {cr}")
            except Exception as e:
                print(f"❌ Erro ao enviar PDF para grupo {grupo_id}, CR {cr}: {str(e)}")
