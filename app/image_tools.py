import os

from flask import current_app
from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .utils.logger import logger
from .utils.timing import measure_duration


@measure_duration
def compress_image(file: FileStorage, quality: int) -> dict:
    """
    Compress an image file to the specified quality.

    Args:
        file: Uploaded image file.
        quality: Compression quality (1-100).

    Return:
        Dictionary containing:
            - filename: Compressed file name
            - path: Absolute path to the compressed image
            - original_size: Original file size in bytes
            - compressed_size: Compressed file size in bytes
            - compression_percentage: Percentage of size reduction
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(file.filename)
    original_path = os.path.join(upload_folder, filename)
    compressed_filename = f"compressed_{filename}"
    compressed_path = os.path.join(upload_folder, compressed_filename)

    try:
        file.save(original_path)
        original_size = os.path.getsize(original_path)

        with Image.open(original_path) as img:
            img.save(compressed_path, optimize=True, quality=quality)

        compressed_size = os.path.getsize(compressed_path)
        compression_percentage = ((original_size - compressed_size) / original_size) * 100

        return {
            "filename": compressed_filename,
            "path": compressed_path,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_percentage": compression_percentage,
        }

    except Exception as exc:
        logger.error(f"Failed to compress {filename}: {exc}", exc_info=True)
        raise
