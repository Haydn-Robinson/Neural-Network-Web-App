"""
The flask application package.
"""

from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = '23d75113a59154178c8aa8ff1f7af914'
    app.config['MANAGER_HOST'] = '127.0.0.1'
    app.config['MANAGER_PORT'] = 22109
    app.config['MANAGER_AUTHKEY'] = b'aaabacadaa'

    #from . import persistence
    #persistence.init_app(app)
    
    from . import views
    app.register_blueprint(views.blueprint)
    
    return app
    