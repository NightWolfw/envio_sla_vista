from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
from config import UPLOAD_FOLDER
from app.services.excel import importar_excel, exportar_excel

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/upload', methods=['POST'])
def upload_file():
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
            file.save(filepath)

            importar_excel(filepath)
            flash('Planilha importada com sucesso!')
        except Exception as e:
            flash(f'Erro ao importar: {str(e)}')

        return redirect(url_for('main.index'))
    else:
        flash('Envie um arquivo .xlsx')
        return redirect(url_for('main.index'))


@bp.route('/export')
def export_file():
    try:
        output = exportar_excel()
        return send_file(
            output,
            as_attachment=True,
            download_name='grupos_export.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        flash(f'Erro ao exportar: {str(e)}')
        return redirect(url_for('main.index'))

@bp.route('/health')
def health():
    return {'status': 'ok', 'timestamp': datetime.now().isoformat()}
