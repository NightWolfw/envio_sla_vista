# gps_bot/api/evolution.py - MÉTODO COMPLETAMENTE ATUALIZADO

import requests
import base64
import mimetypes
import os
from config import EVOLUTION_CONFIG


class EvolutionAPI:
    def __init__(self):
        self.url = EVOLUTION_CONFIG['url']
        self.apikey = EVOLUTION_CONFIG['apikey']
        self.instance = EVOLUTION_CONFIG['instance']

    def enviar_mensagem(self, group_id, mensagem):
        """Envia mensagem de texto"""
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
            if response.status_code in [200, 201]:
                print(f"Mensagem enviada ao grupo {group_id}")
                return True
            else:
                print(f"Falha ao enviar mensagem: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Erro na requisição: {e}")
            return False

    def enviar_arquivo(self, group_id, caminho_arquivo, legenda=""):
        """
        Envia arquivo usando o formato correto da Evolution API v2
        Baseado na documentação: https://doc.evolution-api.com/v2/api-reference/message-controller/send-media
        """
        endpoint = f"{self.url}/message/sendMedia/{self.instance}"
        headers = {
            'apikey': self.apikey,
            'Content-Type': 'application/json'
        }

        try:
            # Verifica se o arquivo existe
            if not os.path.exists(caminho_arquivo):
                print(f"Arquivo não encontrado: {caminho_arquivo}")
                return False

            # Lê o arquivo e converte para base64
            with open(caminho_arquivo, 'rb') as arquivo:
                arquivo_bytes = arquivo.read()
                arquivo_base64 = base64.b64encode(arquivo_bytes).decode('utf-8')

            # Determina o MIME type
            mime_type, _ = mimetypes.guess_type(caminho_arquivo)
            if not mime_type:
                if caminho_arquivo.lower().endswith('.pdf'):
                    mime_type = 'application/pdf'
                else:
                    mime_type = 'application/octet-stream'

            # Determina o mediatype baseado na documentação
            if mime_type.startswith('image/'):
                mediatype = 'image'
            elif mime_type.startswith('video/'):
                mediatype = 'video'
            elif mime_type.startswith('audio/'):
                mediatype = 'audio'
            else:
                mediatype = 'document'  # Para PDFs e outros documentos

            # Nome do arquivo
            nome_arquivo = os.path.basename(caminho_arquivo)

            # Payload conforme documentação Evolution API v2
            payload = {
                "number": group_id,
                "mediatype": mediatype,
                "mimetype": mime_type,
                "caption": legenda,
                "media": arquivo_base64,  # Base64 string do arquivo
                "fileName": nome_arquivo
            }

            # Log para debug
            print(f"📤 Enviando: {nome_arquivo}")
            print(f"   📊 Tamanho: {len(arquivo_bytes)} bytes")
            print(f"   🔧 MIME: {mime_type}")
            print(f"   📱 Media Type: {mediatype}")
            print(f"   🆔 Destino: {group_id}")

            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)

            if response.status_code in [200, 201]:
                print(f"✅ Arquivo enviado com sucesso!")
                try:
                    resp_json = response.json()
                    if 'key' in resp_json:
                        print(f"   🔑 Message Key: {resp_json['key']}")
                except:
                    pass
                return True
            else:
                print(f"❌ Falha ao enviar arquivo:")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")

                # Tenta decodificar a resposta de erro
                try:
                    error_json = response.json()
                    if 'response' in error_json and 'message' in error_json['response']:
                        print(f"   Erro detalhado: {error_json['response']['message']}")
                except:
                    pass

                return False

        except requests.Timeout:
            print(f"⏰ Timeout ao enviar arquivo para {group_id}")
            return False
        except Exception as e:
            print(f"❌ Erro ao enviar arquivo: {e}")
            import traceback
            traceback.print_exc()
            return False
