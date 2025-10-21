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

            # 🔧 CORREÇÃO: Aceitar tanto 200 quanto 201 como sucesso
            # Status 200 = OK (resposta imediata)
            # Status 201 = Created (mensagem aceita e sendo processada)
            if response.status_code in [200, 201]:
                print(f"Mensagem enviada ao grupo {group_id}")

                # Log adicional para status 201
                if response.status_code == 201:
                    try:
                        resp_data = response.json()
                        status = resp_data.get('status', 'N/A')
                        print(f"Status da mensagem: {status} (sendo processada pelo WhatsApp)")
                    except:
                        pass

                return True
            else:
                print(f"Falha ao enviar mensagem ao grupo {group_id}: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Erro na requisição para grupo {group_id}: {e}")
            return False

    def enviar_arquivo(self, group_id, caminho_arquivo, legenda=""):
        """
        Envia um arquivo para grupo via Evolution API.

        :param group_id: ID do grupo no WhatsApp
        :param caminho_arquivo: Caminho para o arquivo
        :param legenda: Legenda opcional do arquivo
        :return: True se envio ocorreu com sucesso, False caso contrário
        """
        endpoint = f"{self.url}/message/sendMedia/{self.instance}"
        headers = {
            'apikey': self.apikey,
        }

        try:
            with open(caminho_arquivo, 'rb') as arquivo:
                files = {
                    'attachment': arquivo
                }
                data = {
                    'number': group_id,
                    'caption': legenda
                }

                response = requests.post(endpoint, headers=headers, files=files, data=data)

                # Aceitar 200 e 201 como sucesso
                if response.status_code in [200, 201]:
                    print(f"Arquivo enviado ao grupo {group_id}")
                    return True
                else:
                    print(f"Falha ao enviar arquivo ao grupo {group_id}: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            print(f"Erro ao enviar arquivo para grupo {group_id}: {e}")
            return False
