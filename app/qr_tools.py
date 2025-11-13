import os
import uuid

import qrcode
from flask import current_app

from .utils.logger import logger
from .utils.timing import measure_duration

DEFAULT_FILL_COLOR = "#6366f1"
DEFAULT_BACKGROUND_COLOR = "#eef2ff"


def _sanitize_hex_color(value: str | None, fallback: str) -> str:
    """
    Ensure the provided color is a valid 7-character hex string.
    """
    if not value:
        return fallback
    color = value.strip()
    if len(color) == 7 and color.startswith("#"):
        hex_digits = "0123456789abcdefABCDEF"
        if all(char in hex_digits for char in color[1:]):
            return color.lower()
    return fallback


@measure_duration
def generate_qr(
    data: str,
    fill_color: str | None = None,
    background_color: str | None = None,
) -> dict:
    """
    Generate a QR code from the given data.

    Args:
        data: Text or URL to encode.
        fill_color: Hex color for the QR modules.
        background_color: Hex color for the QR background.

    Return:
        Dictionary containing:
            - filename: Generated file name
            - path: Absolute file path
            - fill_color: Color used for QR modules
            - background_color: Color used for QR background
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    fill = _sanitize_hex_color(fill_color, DEFAULT_FILL_COLOR)
    background = _sanitize_hex_color(background_color, DEFAULT_BACKGROUND_COLOR)

    filename = f"qr_code_{uuid.uuid4().hex}.png"
    output_path = os.path.join(upload_folder, filename)

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill, back_color=background)
        img.save(output_path)

        return {
            "filename": filename,
            "path": output_path,
            "fill_color": fill,
            "background_color": background,
        }

    except Exception as exc:
        logger.error(f"Failed to generate QR for '{data}': {exc}", exc_info=True)
        raise
