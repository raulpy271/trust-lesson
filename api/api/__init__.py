
from flask import Flask

from api.views import bp
from api import auth


def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.register_blueprint(auth.bp)
    return app
