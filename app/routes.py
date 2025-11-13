import base64
import os

from flask import Blueprint, current_app, render_template, request, send_file
from werkzeug.datastructures import FileStorage

from .image_tools import compress_image
from .qr_tools import (
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_FILL_COLOR,
    generate_qr,
)
from .utils.logger import logger

main = Blueprint("main", __name__)


@main.app_errorhandler(404)
def not_found():
    logger.warning("404 Error: Page not found")
    return render_template("404.html"), 404


@main.app_errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {error}", exc_info=True)
    return render_template("500.html"), 500


@main.route("/")
def index() -> str:
    """
    Render Homepage.
    """
    return render_template("index.html")


@main.route("/compress", methods=["GET", "POST"])
def compress() -> str | FileStorage:
    """
    Handling image compression form and return compressed image.
    """
    if request.method == "POST":
        file = request.files["image"]
        quality = int(request.form.get("quality", 30))
        result = compress_image(file, quality)

        # Format file sizes for display
        original_size_mb = result["original_size"] / (1024 * 1024)
        compressed_size_mb = result["compressed_size"] / (1024 * 1024)
        original_size_kb = result["original_size"] / 1024
        compressed_size_kb = result["compressed_size"] / 1024

        return render_template(
            "compress.html",
            compressed=True,
            download_name=result["filename"],
            original_size_mb=original_size_mb,
            compressed_size_mb=compressed_size_mb,
            original_size_kb=original_size_kb,
            compressed_size_kb=compressed_size_kb,
            compression_percentage=result["compression_percentage"],
        )
    return render_template("compress.html", compressed=False)


@main.route("/download/<filename>")
def download(filename: str):
    """
    Download a compressed image file.
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)
    return send_file(file_path, as_attachment=True)


@main.route("/qr", methods=["GET", "POST"])
def qr() -> str | FileStorage:
    """
    Handle QR generation form and return QR image.
    """
    if request.method == "POST":
        data = request.form["data"]
        fill_color = request.form.get("fill_color", DEFAULT_FILL_COLOR)
        background_color = request.form.get("background_color", DEFAULT_BACKGROUND_COLOR)
        result = generate_qr(data, fill_color=fill_color, background_color=background_color)

        with open(result["path"], "rb") as qr_file:
            encoded = base64.b64encode(qr_file.read()).decode("ascii")
        qr_data_uri = f"data:image/png;base64,{encoded}"

        return render_template(
            "qr.html",
            generated=True,
            qr_data_uri=qr_data_uri,
            download_name=result["filename"],
            original_text=data,
            fill_color=result["fill_color"],
            background_color=result["background_color"],
        )
    return render_template(
        "qr.html",
        generated=False,
        original_text="",
        fill_color=DEFAULT_FILL_COLOR,
        background_color=DEFAULT_BACKGROUND_COLOR,
    )