from flask import Flask
from .routes import main

def create_app() -> Flask:
    """
    Create and configures the Flask application.
    """
    app =Flask(__name__)
    app.config["UPLOAD_FOLDER"] = "static/upload"
    app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024 # 20MB

    app.register_blueprint(main)

    return app
