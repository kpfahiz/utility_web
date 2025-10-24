import os
import qrcode

from .logger import logger
from utils.timing import measure_duration

@measure_duration
def generate_qr(data: str) -> str:
    """
    Generator a QR code from the given data.

    Args:
        data: Text or URL to encode.

    Return:
        Path to the generated QR image.
    """

    output_path = os.path.join("static/uploads", "qr_code.png")

    try:
        img = qrcode.make(data)
        img.save(output_path)

        return output_path

    except Exception as e:
        logger.error(f"Failed to generate QR for '{data}': {e}", exc_info=True)
        raise
