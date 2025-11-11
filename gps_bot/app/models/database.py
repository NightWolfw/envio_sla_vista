import psycopg2
from flask import current_app
from config import DB_SITE_CONFIG, DB_CONFIG

def get_db_vista():
    """Retorna conexão com o banco Vista usando config"""
    return psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )

def get_db_site():
    """Retorna conexão com o banco Site usando config"""
    return psycopg2.connect(
        host=DB_SITE_CONFIG['host'],
        port=DB_SITE_CONFIG['port'],
        database=DB_SITE_CONFIG['database'],
        user=DB_SITE_CONFIG['user'],
        password=DB_SITE_CONFIG['password']
    )
