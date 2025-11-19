import time
from typing import Any, Dict, List, Optional

import requests

from app.models.database import get_db_site
from app.services.estrutura import atualizar_grupo_especifico
import config as project_config

_CACHE_TTL_SECONDS = 180
_grupos_cache: Optional[List[Dict[str, Any]]] = None
_grupos_cache_timestamp: float = 0.0


def buscar_grupos_api() -> list[Dict[str, Any]]:
    """Busca todos os grupos da Evolution API com retry"""
    evolution_config = project_config.EVOLUTION_CONFIG
    instance = evolution_config['instance_name']
    base_url = evolution_config['base_url']
    api_key = evolution_config['api_key']
    
    url = f"{base_url}/group/fetchAllGroups/{instance}"
    headers = {"apikey": api_key}
    params = {"getParticipants": "false"}
    
    max_retries = 3
    timeout = 180  # 3 minutes
    
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Erro ao buscar grupos da API: {response.status_code}")
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                wait_time = 5 * (2 ** (attempt - 1))  # 5s, 10s, 20s
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"Timeout após {max_retries} tentativas. A API não respondeu em {timeout}s.")
        except Exception as e:
            if attempt < max_retries:
                wait_time = 5 * (2 ** (attempt - 1))
                time.sleep(wait_time)
                continue
            else:
                raise

def _get_grupos_api_cached(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Retorna grupos com cache simples em memória"""
    global _grupos_cache, _grupos_cache_timestamp
    now = time.time()
    if (
        not force_refresh
        and _grupos_cache is not None
        and (now - _grupos_cache_timestamp) < _CACHE_TTL_SECONDS
    ):
        return _grupos_cache

    grupos_api = buscar_grupos_api()
    _grupos_cache = grupos_api
    _grupos_cache_timestamp = now
    return grupos_api

def comparar_grupos_novos(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Compara grupos da API com banco e retorna grupos novos"""
    grupos_api = _get_grupos_api_cached(force_refresh=force_refresh)
    
    # Busca IDs já cadastrados no banco
    conn = get_db_site()
    cur = conn.cursor()
    cur.execute("SELECT group_id FROM grupos_whatsapp")
    ids_cadastrados = {row[0] for row in cur.fetchall()}
    cur.close()
    conn.close()
    
    # Filtra apenas grupos novos
    grupos_novos = [
        {
            'group_id': grupo['id'],
            'nome': grupo['subject']
        }
        for grupo in grupos_api
        if grupo['id'] not in ids_cadastrados
    ]
    
    return grupos_novos

def inserir_grupos_novos(grupos_com_cr: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Insere novos grupos no banco com os CRs informados (ou vazio)"""
    conn = get_db_site()
    cur = conn.cursor()
    
    inseridos = 0
    erros = []
    estrutura_atualizada = 0
    
    for grupo in grupos_com_cr:
        try:
            cr = grupo.get('cr')
            # Se CR não informado (vazio/None), define envio=false, senão envio=true
            envio = True if cr else False
            
            cur.execute("""
                INSERT INTO grupos_whatsapp (group_id, nome_grupo, cr, envio, envio_pdf)
                VALUES (%s, %s, %s, %s, FALSE)
                RETURNING id
            """, (grupo['group_id'], grupo['nome'], cr, envio))
            
            grupo_id = cur.fetchone()[0]
            inseridos += 1
            
            # Se tem CR, atualiza estrutura automaticamente
            if cr:
                try:
                    if atualizar_grupo_especifico(grupo_id):
                        estrutura_atualizada += 1
                except Exception as e:
                    print(f"Aviso: Não foi possível atualizar estrutura do grupo {grupo['nome']}: {str(e)}")
                    
        except Exception as e:
            erros.append(f"Erro ao inserir {grupo['nome']}: {str(e)}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {
        'inseridos': inseridos,
        'estrutura_atualizada': estrutura_atualizada,
        'erros': erros
    }

