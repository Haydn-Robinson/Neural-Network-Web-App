"""
The flask application package.
"""

from flask import Flask
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['MANAGER_AUTHKEY'] = bytes(os.environ.get('MANAGER_AUTHKEY'), 'utf8')

    app.config['MANAGER_HOST'] = ''
    #'neural-network-web-app.herokuapp.com'
    app.config['MANAGER_PORT'] = 22109

    from . import views
    app.register_blueprint(views.blueprint)
        
    return app
    