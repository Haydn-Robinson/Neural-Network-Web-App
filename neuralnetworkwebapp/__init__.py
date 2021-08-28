"""
The flask application package.
"""

from flask import Flask
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    from . import views
    app.register_blueprint(views.blueprint)
        
    return app
    