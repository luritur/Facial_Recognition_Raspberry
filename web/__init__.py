import os
from flask import Flask
from core.bd.db import db

from .routes.main_routes import main_bp
from .routes.video_routes import video_bp
from .routes.api_routes import api_bp
from config import Config  # tu archivo de configuración




def create_app():
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    templates_path = os.path.join(BASE_DIR, 'templates')
    static_path = os.path.join(BASE_DIR, 'static')

    app = Flask(__name__, template_folder=templates_path, static_folder=static_path)
    
    # Configuración
    app.config.from_object(Config)

    # Inicializar SQLAlchemy con la app
    db.init_app(app)

    # Importar los modelos antes de crear las tablas
    from core.bd.bd_create import Empleado

    # Crear la BD y tablas si no existen
    with app.app_context():
        db.create_all()
        print("✔ Base de datos y tablas creadas (si no existían)")

    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(api_bp)

    return app
