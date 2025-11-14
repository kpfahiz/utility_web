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


# Supported image formats for conversion
SUPPORTED_FORMATS = {
    "JPEG": {"ext": ".jpg", "name": "JPEG", "supports_alpha": False},
    "PNG": {"ext": ".png", "name": "PNG", "supports_alpha": True},
    "GIF": {"ext": ".gif", "name": "GIF", "supports_alpha": True},
    "BMP": {"ext": ".bmp", "name": "BMP", "supports_alpha": False},
    "TIFF": {"ext": ".tiff", "name": "TIFF", "supports_alpha": True},
    "WEBP": {"ext": ".webp", "name": "WebP", "supports_alpha": True},
    "ICO": {"ext": ".ico", "name": "ICO", "supports_alpha": True},
}


@measure_duration
def convert_image(file: FileStorage, target_format: str, quality: int = 95) -> dict:
    """
    Convert an image file to a different format.

    Args:
        file: Uploaded image file.
        target_format: Target format (JPEG, PNG, GIF, BMP, TIFF, WEBP, ICO).
        quality: Quality for lossy formats like JPEG/WebP (1-100).

    Returns:
        Dictionary containing:
            - filename: Converted file name
            - path: Absolute path to the converted image
            - original_format: Original image format
            - target_format: Target image format
            - original_size: Original file size in bytes
            - converted_size: Converted file size in bytes
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(file.filename)
    original_path = os.path.join(upload_folder, filename)
    
    # Get base filename without extension
    base_name = os.path.splitext(filename)[0]
    
    # Get target format info
    if target_format.upper() not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {target_format}")
    
    format_info = SUPPORTED_FORMATS[target_format.upper()]
    target_ext = format_info["ext"]
    converted_filename = f"converted_{base_name}{target_ext}"
    converted_path = os.path.join(upload_folder, converted_filename)

    try:
        file.save(original_path)
        original_size = os.path.getsize(original_path)

        with Image.open(original_path) as img:
            original_format = img.format or "UNKNOWN"
            
            # Convert RGBA to RGB for formats that don't support alpha channel
            if img.mode in ("RGBA", "LA", "P") and not format_info["supports_alpha"]:
                # Create a white background
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                if img.mode in ("RGBA", "LA"):
                    background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                img = background
            elif img.mode == "P" and format_info["supports_alpha"]:
                img = img.convert("RGBA")
            elif img.mode == "P":
                img = img.convert("RGB")
            
            # Prepare save options
            save_kwargs = {}
            if target_format.upper() in ("JPEG", "WEBP"):
                save_kwargs["quality"] = quality
                save_kwargs["optimize"] = True
            elif target_format.upper() == "PNG":
                save_kwargs["optimize"] = True
            elif target_format.upper() == "TIFF":
                save_kwargs["compression"] = "tiff_lzw"
            
            # Save in target format
            img.save(converted_path, format=target_format.upper(), **save_kwargs)

        converted_size = os.path.getsize(converted_path)

        return {
            "filename": converted_filename,
            "path": converted_path,
            "original_format": original_format,
            "target_format": target_format.upper(),
            "original_size": original_size,
            "converted_size": converted_size,
        }

    except Exception as exc:
        logger.error(f"Failed to convert {filename} to {target_format}: {exc}", exc_info=True)
        raise