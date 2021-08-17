"""
The flask application package.
"""

from flask import Flask
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['MANAGER_AUTHKEY'] = bytes(os.environ.get('MANAGER_AUTHKEY'), 'utf8')

    if os.environ.get('ON_HEROKU') == 'True':
        app.config['MANAGER_PORT'] = int(os.environ.get("PORT"))
        app.config['MANAGER_HOST'] = '0.0.0.0'
    else:
        app.config['MANAGER_HOST'] = '127.0.0.1'
        app.config['MANAGER_PORT'] = 22109

    from . import views
    app.register_blueprint(views.blueprint)
        
    return app
    