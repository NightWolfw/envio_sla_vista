import psycopg2
from flask import current_app


def get_db_vista():
    """Retorna conexão com PostgreSQL (Vista - dw_gps)"""
    try:
        config = current_app.config['DB_CONFIG']
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar com Vista: {e}")
        raise


def get_db_site():
    """Retorna conexão com PostgreSQL (Site - dw_sla)"""
    try:
        config = current_app.config['DB_SITE_CONFIG']
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar com Site: {e}")
        raise
