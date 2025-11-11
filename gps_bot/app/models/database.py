import psycopg2
from app import create_app
from config import DB_SITE_CONFIG

app = create_app()

def get_db_vista():
    config = app.config['DB_CONFIG']
    return psycopg2.connect(
        host=config['host'],
        port=config['port'],
        database=config['database'],
        user=config['user'],
        password=config['password']
    )

def get_db_site():
    return psycopg2.connect(
        host=DB_SITE_CONFIG['host'],
        port=DB_SITE_CONFIG['port'],
        database=DB_SITE_CONFIG['database'],
        user=DB_SITE_CONFIG['user'],
        password=DB_SITE_CONFIG['password']
    )
