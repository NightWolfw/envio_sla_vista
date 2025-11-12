from flask import Flask
import logging
import os
import config

def create_app():
    app = Flask(__name__)

    # Logging básico
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Configurações gerais
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

    # Configurações de banco de dados
    app.config['DB_CONFIG'] = config.DB_CONFIG
    app.config['DB_SITE_CONFIG'] = config.DB_SITE_CONFIG

    # Configurações da Evolution API
    app.config['EVOLUTION_CONFIG'] = config.EVOLUTION_CONFIG

    # Importa e registra blueprints
    from app.routes.main import bp as main_bp
    from app.routes.grupos import bp as grupos_bp
    from app.routes.mensagens import bp as mensagens_bp
    from app.routes.envio import bp as envio_bp
    from app.routes.sla import bp as sla_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(grupos_bp)
    app.register_blueprint(mensagens_bp)
    app.register_blueprint(envio_bp)
    app.register_blueprint(sla_bp)

    # ✅ CORREÇÃO: Só inicia scheduler no processo principal (não no reloader)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        with app.app_context():
            from app.services.scheduler_service import iniciar_scheduler
            iniciar_scheduler(app)

    return app

# Se você rodar diretamente este arquivo
if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='0.0.0.0')
