"""
Configurações do projeto envio_sla_vista
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]

# ===== CONFIGURA
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
PDF_STORAGE_DIR = Path(os.getenv('PDF_STORAGE_DIR', str(BASE_DIR / 'temp_pdfs'))).resolve()

# ===== BANCO DE DADOS VISTA (dw_gps) =====
DB_CONFIG = {
    'host': os.getenv('DB_VISTA_HOST', 'localhost'),
    'port': int(os.getenv('DB_VISTA_PORT', 5432)),
    'database': os.getenv('DB_VISTA_DATABASE', 'dw_gps'),
    'user': os.getenv('DB_VISTA_USER', 'postgres'),
    'password': os.getenv('DB_VISTA_PASSWORD', 'postgres')
}

# ===== BANCO DE DADOS SITE (dw_sla) =====
DB_SITE_CONFIG = {
    'host': os.getenv('DB_SITE_HOST', 'localhost'),
    'port': int(os.getenv('DB_SITE_PORT', 5432)),
    'database': os.getenv('DB_SITE_DATABASE', 'dw_sla'),
    'user': os.getenv('DB_SITE_USER', 'postgres'),
    'password': os.getenv('DB_SITE_PASSWORD', 'postgres')
}

# ===== EVOLUTION API (WhatsApp) =====
EVOLUTION_CONFIG = {
    'base_url': os.getenv('EVOLUTION_BASE_URL', 'http://localhost:8080'),
    'api_key': os.getenv('EVOLUTION_API_KEY', 'your-api-key-here'),
    'instance_name': os.getenv('EVOLUTION_INSTANCE_NAME', 'instance1')
}


# ===== URL pública para links de relatórios =====
PUBLIC_API_BASE_URL = os.getenv('PUBLIC_API_BASE_URL', 'http://localhost:5000').rstrip('/')

# ===== HORÁRIOS DE ENVIO (para scheduler legado) =====
HORARIOS_ENVIO = os.getenv('HORARIOS_ENVIO', '08:00,12:00,18:00').split(',')

# ===== DEBUG =====
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

