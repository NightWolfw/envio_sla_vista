from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from config import UPLOAD_FOLDER
from app.services.excel import importar_excel, exportar_excel
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


@bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload e importação de planilha Excel"""
    if 'file' not in request.files:
        flash('Nenhum arquivo enviado')
        return redirect(url_for('main.index'))

    file = request.files['file']

    if file.filename == '':
        flash('Nenhum arquivo selecionado')
        return redirect(url_for('main.index'))

    if file and file.filename.endswith('.xlsx'):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            # Cria pasta de upload se não existir
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            file.save(filepath)

            resultado = importar_excel(filepath)
            flash(
                f'✅ Importação concluída! {resultado["importados"]} novos, {resultado["atualizados"]} atualizados, {resultado["erros"]} erros')
        except Exception as e:
            flash(f'❌ Erro ao importar: {str(e)}')

        return redirect(url_for('main.index'))
    else:
        flash('⚠️ Envie um arquivo .xlsx')
        return redirect(url_for('main.index'))


@bp.route('/export')
def export_file():
    """Exporta grupos para planilha Excel"""
    try:
        output = exportar_excel()
        return send_file(
            output,
            as_attachment=True,
            download_name='grupos_export.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        flash(f'❌ Erro ao exportar: {str(e)}')
        return redirect(url_for('main.index'))


@bp.route('/health')
def health():
    """Endpoint de healthcheck"""
    return {'status': 'ok', 'timestamp': datetime.now().isoformat()}
