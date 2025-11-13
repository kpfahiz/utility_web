import os

from flask import Flask

from .routes import main


def create_app() -> Flask:
    """
    Create and configures the Flask application.
    """
    app = Flask(__name__)
    upload_folder = os.path.join(app.root_path, "..", "static", "uploads")
    upload_folder = os.path.normpath(upload_folder)
    os.makedirs(upload_folder, exist_ok=True)

    app.config["UPLOAD_FOLDER"] = upload_folder
    app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB

    app.register_blueprint(main)

    return app
