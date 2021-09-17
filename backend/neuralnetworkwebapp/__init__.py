"""
The flask application package.
"""

from flask import Flask
from flask_cors import CORS
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    CORS(app)

    from . import views
    app.register_blueprint(views.api)
    app.register_blueprint(views.public_routes)
        
    return app
    