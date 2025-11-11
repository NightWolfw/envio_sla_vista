import requests
from app import create_app

app = create_app()

def enviar_mensagem(group_id, mensagem):
    config = app.config['EVOLUTION_CONFIG']
    url = f"{config['url']}/message/sendText/{config['instance']}"

    headers = {
        'Content-Type': 'application/json',
        'apikey': config['apikey']
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
