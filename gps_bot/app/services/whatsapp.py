"""
Service para integração com Evolution API WhatsApp
"""
import requests
import base64
from flask import current_app
import logging

logger = logging.getLogger(__name__)


def get_evolution_config():
    """Retorna configuração da Evolution API"""
    return {
        'base_url': current_app.config['EVOLUTION_CONFIG']['base_url'],
        'api_key': current_app.config['EVOLUTION_CONFIG']['api_key'],
        'instance_name': current_app.config['EVOLUTION_CONFIG']['instance_name']
    }


def enviar_mensagem_texto(group_id, mensagem):
    """
    Envia mensagem de texto para um grupo WhatsApp

    Args:
        group_id: ID do grupo WhatsApp (ex: '120363xxxxxx@g.us')
        mensagem: Texto da mensagem

    Returns:
        dict com resposta da API
    """
    try:
        config = get_evolution_config()

        url = f"{config['base_url']}/message/sendText/{config['instance_name']}"

        headers = {
            'Content-Type': 'application/json',
            'apikey': config['api_key']
        }

        payload = {
            'number': group_id,
            'text': mensagem
        }

        logger.info(f"Enviando mensagem para grupo {group_id}")

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        resultado = response.json()
        logger.info(f"Mensagem enviada com sucesso: {resultado}")

        return resultado

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        raise Exception(f"Erro ao enviar mensagem: {str(e)}")


def enviar_mensagem(group_id, mensagem):
    """
    Envia mensagem de texto para um grupo WhatsApp
    Retorna tupla (sucesso: bool, erro: str ou None) para compatibilidade com código antigo

    Args:
        group_id: ID do grupo WhatsApp
        mensagem: Texto da mensagem

    Returns:
        tuple: (True, None) se sucesso ou (False, mensagem_erro) se falhar
    """
    try:
        resultado = enviar_mensagem_texto(group_id, mensagem)
        return (True, None)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Erro ao enviar mensagem para {group_id}: {error_msg}")
        return (False, error_msg)


def enviar_pdf_whatsapp(group_id, caminho_pdf, caption=''):
    """
    Envia arquivo PDF para um grupo WhatsApp

    Args:
        group_id: ID do grupo WhatsApp
        caminho_pdf: Caminho completo do arquivo PDF
        caption: Legenda do arquivo (opcional)

    Returns:
        dict com resposta da API
    """
    try:
        config = get_evolution_config()

        # Lê o arquivo PDF e converte para base64
        with open(caminho_pdf, 'rb') as pdf_file:
            pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')

        url = f"{config['base_url']}/message/sendMedia/{config['instance_name']}"

        headers = {
            'Content-Type': 'application/json',
            'apikey': config['api_key']
        }

        # Nome do arquivo
        filename = caminho_pdf.split('/')[-1].split('\\')[-1]

        payload = {
            'number': group_id,
            'mediatype': 'document',
            'mimetype': 'application/pdf',
            'caption': caption,
            'fileName': filename,
            'media': pdf_base64
        }

        logger.info(f"Enviando PDF {filename} para grupo {group_id}")

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()

        resultado = response.json()
        logger.info(f"PDF enviado com sucesso: {resultado}")

        return resultado

    except FileNotFoundError:
        logger.error(f"Arquivo PDF não encontrado: {caminho_pdf}")
        raise Exception(f"Arquivo PDF não encontrado: {caminho_pdf}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar PDF: {e}")
        raise Exception(f"Erro ao enviar PDF: {str(e)}")


def enviar_pdf_mensagem(grupos_ids, mensagem, pdf_path):
    """
    Envia mensagem + PDF para múltiplos grupos (compatibilidade com código antigo)

    Args:
        grupos_ids: Lista de IDs dos grupos
        mensagem: Mensagem de texto
        pdf_path: Caminho do PDF

    Returns:
        dict com resultados
    """
    resultados = []

    for group_id in grupos_ids:
        try:
            # Envia mensagem
            msg_result = enviar_mensagem_texto(group_id, mensagem)

            # Envia PDF
            pdf_result = enviar_pdf_whatsapp(group_id, pdf_path, 'Relatório SLA')

            resultados.append({
                'group_id': group_id,
                'sucesso': True,
                'mensagem': msg_result,
                'pdf': pdf_result
            })

        except Exception as e:
            resultados.append({
                'group_id': group_id,
                'sucesso': False,
                'erro': str(e)
            })

    return resultados


def enviar_arquivo(group_id, caminho_arquivo, caption='', mimetype='application/pdf'):
    """
    Envia arquivo genérico para um grupo WhatsApp

    Args:
        group_id: ID do grupo WhatsApp
        caminho_arquivo: Caminho completo do arquivo
        caption: Legenda do arquivo (opcional)
        mimetype: Tipo MIME do arquivo

    Returns:
        dict com resposta da API
    """
    try:
        config = get_evolution_config()

        # Lê o arquivo e converte para base64
        with open(caminho_arquivo, 'rb') as file:
            file_base64 = base64.b64encode(file.read()).decode('utf-8')

        url = f"{config['base_url']}/message/sendMedia/{config['instance_name']}"

        headers = {
            'Content-Type': 'application/json',
            'apikey': config['api_key']
        }

        # Nome do arquivo
        filename = caminho_arquivo.split('/')[-1].split('\\')[-1]

        payload = {
            'number': group_id,
            'mediatype': 'document',
            'mimetype': mimetype,
            'caption': caption,
            'fileName': filename,
            'media': file_base64
        }

        logger.info(f"Enviando arquivo {filename} para grupo {group_id}")

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()

        resultado = response.json()
        logger.info(f"Arquivo enviado com sucesso: {resultado}")

        return resultado

    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
        raise Exception(f"Arquivo não encontrado: {caminho_arquivo}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar arquivo: {e}")
        raise Exception(f"Erro ao enviar arquivo: {str(e)}")


def verificar_conexao_instance():
    """
    Verifica se a instância da Evolution API está conectada

    Returns:
        dict com status da conexão
    """
    try:
        config = get_evolution_config()

        url = f"{config['base_url']}/instance/connectionState/{config['instance_name']}"

        headers = {
            'apikey': config['api_key']
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Erro ao verificar conexão: {e}")
        return {'state': 'disconnected', 'error': str(e)}
