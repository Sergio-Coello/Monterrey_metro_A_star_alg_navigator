from flask import Flask
import webbrowser

import grafo


graph = grafo.crear_grafo()


def create_app():
    app = Flask(__name__)

    from .views import views

    app.register_blueprint(views)
    webbrowser.open_new("http://127.0.0.1:5000")
    return app
