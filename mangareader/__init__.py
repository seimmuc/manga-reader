from flask import Flask

from mangareader import manga


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(manga.bp)
    manga.init(app)
    return app
