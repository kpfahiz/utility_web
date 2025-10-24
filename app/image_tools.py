import os

from PIL import Image
from werkzeug.datastructures import FileStorage

def compress_image(file: FileStorage, quality: int) -> str:
    """
    Compress an image file to the specified quality.
    
    Args:
        file: Uploaded image file.
        quality: Compression quality (1-100).

    Return:
        Path to the compressed image.
    """
    filename = file.filename
    filepath = os.path.join("static/uploads", filename)
    file.save(filepath)

    img = Image.open(filepath)
    compressed_path = os.path.join("static/uploads", f"compressed_{filename}")
    img.save(compressed_path, optimize=True, quality=quality)

    return compressed_path