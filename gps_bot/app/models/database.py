import psycopg2
from config import DB_CONFIG, DB_SITE_CONFIG

def get_db_site():
    """Retorna conexão com banco dw_sla (site admin)"""
    return psycopg2.connect(
        dbname=DB_SITE_CONFIG['database'],
        user=DB_SITE_CONFIG['user'],
        password=DB_SITE_CONFIG['password'],
        host=DB_SITE_CONFIG['host'],
        port=DB_SITE_CONFIG['port']
    )

def get_db_vista():
    """Retorna conexão com banco dw_gps (Vista)"""
    return psycopg2.connect(
        dbname=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )
