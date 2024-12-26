
from flask import Flask

from api.views import bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app
