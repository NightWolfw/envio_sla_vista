import requests
from config import EVOLUTION_CONFIG


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
