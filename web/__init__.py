
import os
from flask import Flask
from .routes.main_routes import main_bp
from .routes.video_routes import video_bp
from .routes.api_routes import api_bp

def create_app():
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # project/
    templates_path = os.path.join(BASE_DIR, 'templates')  # project/templates

    app = Flask(__name__, template_folder=templates_path, static_folder=os.path.join(BASE_DIR, 'static'))

    app.register_blueprint(main_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(api_bp)

    return app