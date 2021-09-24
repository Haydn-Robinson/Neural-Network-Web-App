"""
The flask application package.
"""

from flask import Flask
from flask_cors import CORS
import os


def create_app():
    app = Flask(__name__,
    instance_relative_config=True,
    static_folder='../../frontend/build',
    static_url_path="/")

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    if os.environ.get('HTTPS') == 'True':
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_SECURE'] = 'Lax'
    CORS(app)

    from . import views
    app.register_blueprint(views.api)
    app.register_blueprint(views.public_routes)
        
    return app
    