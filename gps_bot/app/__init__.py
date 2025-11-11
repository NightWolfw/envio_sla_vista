from flask import Flask
import os


def create_app():
    app = Flask(__name__)

    # Carrega configurações
    app.config.from_object('config')

    # Cria diretório de uploads se não existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Registra blueprints (rotas)
    from app.routes import main, grupos, mensagens, envio
    app.register_blueprint(main.bp)
    app.register_blueprint(grupos.bp)
    app.register_blueprint(mensagens.bp)
    app.register_blueprint(envio.bp)

    return app
