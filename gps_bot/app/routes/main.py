from flask import Blueprint, render_template
from datetime import datetime
from app.models.database import get_db_site

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Página inicial com estatísticas"""
    try:
        conn = get_db_site()
        cur = conn.cursor()

        # Total de grupos
        cur.execute("SELECT COUNT(*) FROM grupos_whatsapp")
        total_grupos = cur.fetchone()[0]

        # Total de mensagens agendadas ativas
        cur.execute("SELECT COUNT(*) FROM mensagens WHERE ativo = true")
        total_mensagens = cur.fetchone()[0]

        # Total de envios realizados
        cur.execute("SELECT COUNT(*) FROM logs_envio")
        total_envios = cur.fetchone()[0]

        cur.close()
        conn.close()

        return render_template('index.html',
                               total_grupos=total_grupos,
                               total_mensagens=total_mensagens,
                               total_envios=total_envios)
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {str(e)}")
        return render_template('index.html')


@bp.route('/health')
def health():
    """Endpoint de healthcheck"""
    return {'status': 'ok', 'timestamp': datetime.now().isoformat()}
