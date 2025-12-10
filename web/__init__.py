
import os
from flask import Flask
from .routes.main_routes import main_bp
from .routes.video_routes import video_bp
from .routes.api_routes import api_bp
from flask_socketio import SocketIO


# Creamos SocketIO global
socketio = SocketIO()

def create_app():
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # project/
    templates_path = os.path.join(BASE_DIR, 'templates')
    static_path = os.path.join(BASE_DIR, 'static')

    app = Flask(__name__, template_folder=templates_path, static_folder=static_path)

    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(api_bp)

    # Inicializar SocketIO con la app
    socketio.init_app(app)

    return app