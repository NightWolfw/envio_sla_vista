import requests
from config import EVOLUTION_CONFIG


class EvolutionAPI:
    def __init__(self):
        self.url = EVOLUTION_CONFIG['url']
        self.apikey = EVOLUTION_CONFIG['apikey']
        self.instance = EVOLUTION_CONFIG['instance']

    def enviar_mensagem(self, group_id, mensagem):
        """
        Envia uma mensagem de texto para grupo via Evolution API.

        :param group_id: ID do grupo no WhatsApp
        :param mensagem: Texto da mensagem a enviar
        :return: True se envio ocorreu com sucesso, False caso contrário
        """
        endpoint = f"{self.url}/message/sendText/{self.instance}"
        headers = {
            'apikey': self.apikey,
            'Content-Type': 'application/json'
        }
        payload = {
            'number': group_id,
            'text': mensagem
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"Mensagem enviada ao grupo {group_id}")
                return True
            else:
                print(f"Falha ao enviar mensagem ao grupo {group_id}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Erro na requisição para grupo {group_id}: {e}")
            return False
