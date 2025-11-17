from __future__ import annotations

import time
from typing import Any, Mapping

import psycopg2
from psycopg2.extensions import connection

from gps_bot import config as project_config


def conectar_com_retry(
    config: Mapping[str, Any],
    max_tentativas: int = 5,
    delay_inicial: int = 2,
    db_nome: str = "Vista",
) -> connection:
    """
    Tenta conectar ao banco com retry automático
    
    Args:
        config: Dicionário com configurações do banco
        max_tentativas: Número máximo de tentativas (padrão: 5)
        delay_inicial: Delay inicial em segundos (padrão: 2s)
        db_nome: Nome do banco para logging
    
    Returns:
        Conexão psycopg2
    
    Raises:
        Exception: Se todas as tentativas falham
    """
    ultima_exception = None
    delay = delay_inicial
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            print(f"[{db_nome}] Tentativa {tentativa}/{max_tentativas} de conexão...")
            
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['user'],
                password=config['password'],
                connect_timeout=10  # Timeout de 10 segundos por tentativa
            )
            
            print(f"[{db_nome}] ✅ Conexão estabelecida com sucesso!")
            return conn
            
        except (psycopg2.OperationalError, psycopg2.DatabaseError, Exception) as e:
            ultima_exception = e
            print(f"[{db_nome}] ❌ Tentativa {tentativa} falhou: {str(e)}")
            
            if tentativa < max_tentativas:
                print(f"[{db_nome}] ⏳ Aguardando {delay}s antes da próxima tentativa...")
                time.sleep(delay)
                # Aumenta o delay progressivamente (backoff exponencial limitado)
                delay = min(delay * 1.5, 10)  # Máximo de 10s entre tentativas
            else:
                print(f"[{db_nome}] 🚫 Todas as {max_tentativas} tentativas falharam!")
    
    # Se chegou aqui, todas as tentativas falharam
    raise Exception(f"Não foi possível conectar ao banco {db_nome} após {max_tentativas} tentativas. Último erro: {str(ultima_exception)}")


def get_db_vista() -> connection:
    """Retorna conexão com PostgreSQL (Vista - dw_gps) com retry automático"""
    config: Mapping[str, Any] = project_config.DB_CONFIG
    return conectar_com_retry(
        config,
        max_tentativas=5,
        delay_inicial=2,
        db_nome="Vista",
    )


def get_db_site() -> connection:
    """Retorna conexão com PostgreSQL (Site - dw_sla) com retry automático"""
    config: Mapping[str, Any] = project_config.DB_SITE_CONFIG
    return conectar_com_retry(
        config,
        max_tentativas=5,
        delay_inicial=2,
        db_nome="Site",
    )
