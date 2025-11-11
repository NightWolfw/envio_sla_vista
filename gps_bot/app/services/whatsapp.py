"""
Serviço de integração com Evolution API (WhatsApp)
Funções para enviar mensagens de texto e arquivos PDF
"""
import requests
from config import EVOLUTION_CONFIG
from app.models.sla import buscar_tarefas_para_sla
from app.services.pdf_generator import gerar_pdf_sla


def enviar_mensagem(group_id, mensagem):
    """
    Envia mensagem de texto via Evolution API

    Args:
        group_id: ID do grupo WhatsApp
        mensagem: Texto da mensagem

    Returns:
        Tuple (sucesso: bool, erro: str ou None)
    """
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
        print(f"✅ Mensagem enviada para {group_id}")
        return True, None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao enviar mensagem para {group_id}: {str(e)}")
        return False, str(e)
    except Exception as e:
        print(f"❌ Erro inesperado ao enviar mensagem: {str(e)}")
        return False, str(e)


def enviar_pdf_mensagem(grupo_id, mensagem, cr_list, data_inicio, data_fim, tipos_tarefa):
    """
    Gera PDF do SLA e envia via Evolution API

    Args:
        grupo_id: ID do grupo WhatsApp
        mensagem: Mensagem que acompanha o PDF
        cr_list: Lista de CRs para buscar tarefas
        data_inicio: Data inicial do período (formato: YYYY-MM-DD)
        data_fim: Data final do período (formato: YYYY-MM-DD)
        tipos_tarefa: Lista de tipos (abertas, iniciadas, finalizadas)

    Returns:
        Tuple (sucesso: bool, erro: str ou None)
    """
    for cr in cr_list:
        try:
            # Busca tarefas do banco Vista
            tarefas = buscar_tarefas_para_sla([cr], data_inicio, data_fim, tipos_tarefa)

            if not tarefas:
                print(f"⚠️ Nenhuma tarefa encontrada para CR {cr}")
                continue

            # Extrai nome do contrato
            contrato_nome = tarefas[0][0]
            periodo_str = f"{data_inicio} até {data_fim}"

            # Gera PDF
            pdf_bytes = gerar_pdf_sla(tarefas, cr, contrato_nome, periodo_str)

            # Envia PDF via Evolution API
            url = f"{EVOLUTION_CONFIG['url']}/message/sendMedia/{EVOLUTION_CONFIG['instance']}"

            headers = {
                'apikey': EVOLUTION_CONFIG['apikey']
            }

            files = {
                'number': (None, grupo_id),
                'caption': (None, mensagem),
                'media': (f'sla_{cr}.pdf', pdf_bytes, 'application/pdf')
            }

            response = requests.post(url, headers=headers, files=files, timeout=30)
            response.raise_for_status()

            print(f"✅ PDF enviado para grupo {grupo_id}, CR {cr}")
            return True, None

        except Exception as e:
            erro_msg = f"Erro ao enviar PDF para grupo {grupo_id}, CR {cr}: {str(e)}"
            print(f"❌ {erro_msg}")
            return False, erro_msg

    return False, "Nenhum PDF foi gerado"


def enviar_arquivo(group_id, arquivo_path, caption=""):
    """
    Envia arquivo genérico via Evolution API

    Args:
        group_id: ID do grupo WhatsApp
        arquivo_path: Caminho do arquivo a ser enviado
        caption: Legenda do arquivo (opcional)

    Returns:
        Tuple (sucesso: bool, erro: str ou None)
    """
    url = f"{EVOLUTION_CONFIG['url']}/message/sendMedia/{EVOLUTION_CONFIG['instance']}"

    headers = {
        'apikey': EVOLUTION_CONFIG['apikey']
    }

    try:
        with open(arquivo_path, 'rb') as f:
            files = {
                'number': (None, group_id),
                'caption': (None, caption),
                'media': (arquivo_path.split('/')[-1], f, 'application/octet-stream')
            }

            response = requests.post(url, headers=headers, files=files, timeout=30)
            response.raise_for_status()

            print(f"✅ Arquivo enviado para {group_id}")
            return True, None

    except Exception as e:
        print(f"❌ Erro ao enviar arquivo para {group_id}: {str(e)}")
        return False, str(e)


def testar_conexao():
    """
    Testa conexão com Evolution API

    Returns:
        bool: True se conectado, False caso contrário
    """
    url = f"{EVOLUTION_CONFIG['url']}/instance/connectionState/{EVOLUTION_CONFIG['instance']}"

    headers = {
        'apikey': EVOLUTION_CONFIG['apikey']
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ Conexão com Evolution API OK")
        return True
    except Exception as e:
        print(f"❌ Falha na conexão com Evolution API: {str(e)}")
        return False
