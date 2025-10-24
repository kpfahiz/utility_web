from flask import Blueprint, render_template, request, send_file
from werkzeug.datastructures import FileStorage
from .image_tools import compress_image
from .qr_tools import generate_qr
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
def compress() ->str | FileStorage:
    """
    Handling image compression form and return compressed image.
    """
    if request.method == "POST":
        file = request.files["image"]
        quality = int(request.form.get("quality", 30))
        output_path = compress_image(file, quality)
        return send_file(output_path, as_attachment=True)
    return render_template("comprerss.html")

@main.route("/qr", methods=["GET", "POST"])
def qr()-> str | FileStorage:
    """
    Handle QR generation form and return QR image.
    """
    if request.method == "POST":
        data = request.form["data"]
        output_path = generate_qr(data)
        return send_file(output_path, as_attachment=True)
    return render_template("qr.html")

