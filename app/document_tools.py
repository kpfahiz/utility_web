import os
import time
import uuid

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .utils.logger import logger
from .utils.timing import measure_duration

try:
    from pdf2docx import Converter
    PDF2DOCX_AVAILABLE = True
except ImportError:
    PDF2DOCX_AVAILABLE = False

try:
    from docx2pdf import convert
    DOCX2PDF_AVAILABLE = True
except ImportError:
    DOCX2PDF_AVAILABLE = False


@measure_duration
def convert_pdf_to_doc(file: FileStorage) -> dict:
    """
    Convert a PDF file to DOCX format.

    Args:
        file: Uploaded PDF file.

    Returns:
        Dictionary containing:
            - filename: Converted file name
            - path: Absolute path to the converted DOCX file
            - original_size: Original file size in bytes
            - converted_size: Converted file size in bytes
    """
    if not PDF2DOCX_AVAILABLE:
        raise ImportError(
            "pdf2docx library is not installed. Please install it using: pip install pdf2docx"
        )

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(file.filename)

    # Get base filename without extension and add unique identifier
    base_name = os.path.splitext(filename)[0]
    unique_id = uuid.uuid4().hex[:8]
    converted_filename = f"converted_{base_name}_{unique_id}.docx"
    converted_path = os.path.join(upload_folder, converted_filename)
    original_path = os.path.join(upload_folder, f"{unique_id}_{filename}")

    try:
        file.save(original_path)
        original_size = os.path.getsize(original_path)

        # Delete output file if it exists (to avoid permission issues)
        if os.path.exists(converted_path):
            try:
                os.remove(converted_path)
                time.sleep(0.1)  # Small delay to ensure file is released
            except Exception as e:
                logger.warning(f"Could not remove existing file {converted_path}: {e}")

        # Convert PDF to DOCX
        cv = Converter(original_path)
        cv.convert(converted_path, start=0, end=None)
        cv.close()

        # Clean up original file
        try:
            if os.path.exists(original_path):
                os.remove(original_path)
        except Exception as e:
            logger.warning(f"Could not remove temporary file {original_path}: {e}")

        # Wait a moment for file system to catch up
        time.sleep(0.1)

        if not os.path.exists(converted_path):
            raise Exception("Conversion completed but output file was not created")

        converted_size = os.path.getsize(converted_path)

        return {
            "filename": converted_filename,
            "path": converted_path,
            "original_size": original_size,
            "converted_size": converted_size,
        }

    except Exception as exc:
        logger.error(f"Failed to convert PDF {filename} to DOCX: {exc}", exc_info=True)
        # Clean up on error
        try:
            if os.path.exists(original_path):
                os.remove(original_path)
            if os.path.exists(converted_path):
                os.remove(converted_path)
        except Exception:
            pass
        raise


@measure_duration
def convert_doc_to_pdf(file: FileStorage) -> dict:
    """
    Convert a DOCX file to PDF format preserving all formatting, images, and styles.

    Args:
        file: Uploaded DOCX file.

    Returns:
        Dictionary containing:
            - filename: Converted file name
            - path: Absolute path to the converted PDF file
            - original_size: Original file size in bytes
            - converted_size: Converted file size in bytes
    """
    if not DOCX2PDF_AVAILABLE:
        raise ImportError(
            "docx2pdf library is not installed. Please install it using: "
            "pip install docx2pdf\n\n"
            "Note: This library requires LibreOffice or Microsoft Word to be installed.\n"
            "For Windows: Install Microsoft Word or LibreOffice\n"
            "For Linux/Mac: Install LibreOffice (sudo apt-get install libreoffice)"
        )

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(file.filename)

    # Get base filename without extension and add unique identifier
    base_name = os.path.splitext(filename)[0]
    unique_id = uuid.uuid4().hex[:8]
    converted_filename = f"converted_{base_name}_{unique_id}.pdf"
    converted_path = os.path.join(upload_folder, converted_filename)
    original_path = os.path.join(upload_folder, f"{unique_id}_{filename}")

    try:
        file.save(original_path)
        original_size = os.path.getsize(original_path)

        # Delete output file if it exists (to avoid permission issues)
        if os.path.exists(converted_path):
            try:
                os.remove(converted_path)
                time.sleep(0.1)  # Small delay to ensure file is released
            except Exception as e:
                logger.warning(f"Could not remove existing file {converted_path}: {e}")

        # Convert DOCX to PDF using docx2pdf
        # This preserves all formatting, images, alignment, fonts, and styles
        convert(original_path, converted_path)

        # Clean up original file
        try:
            if os.path.exists(original_path):
                os.remove(original_path)
        except Exception as e:
            logger.warning(f"Could not remove temporary file {original_path}: {e}")

        # Wait a moment for file system to catch up
        time.sleep(0.1)

        if not os.path.exists(converted_path):
            raise Exception("Conversion completed but output file was not created")

        converted_size = os.path.getsize(converted_path)

        return {
            "filename": converted_filename,
            "path": converted_path,
            "original_size": original_size,
            "converted_size": converted_size,
        }

    except Exception as exc:
        logger.error(f"Failed to convert DOCX {filename} to PDF: {exc}", exc_info=True)
        # Clean up on error
        try:
            if os.path.exists(original_path):
                os.remove(original_path)
            if os.path.exists(converted_path):
                os.remove(converted_path)
        except Exception:
            pass
        
        # Provide helpful error message
        error_msg = str(exc)
        if "LibreOffice" in error_msg or "soffice" in error_msg.lower():
            raise Exception(
                "LibreOffice is required but not found. Please install LibreOffice:\n"
                "Windows: Download from https://www.libreoffice.org/\n"
                "Linux: sudo apt-get install libreoffice\n"
                "Mac: brew install --cask libreoffice"
            )
        elif "Word" in error_msg or "win32com" in error_msg.lower():
            raise Exception(
                "Microsoft Word is required but not found. Please install Microsoft Word "
                "or use LibreOffice as an alternative."
            )
        elif "Permission denied" in error_msg or "[Errno 13]" in error_msg:
            raise Exception(
                f"Permission denied while accessing file. This may happen if:\n"
                "1. The file is open in another program (Word/LibreOffice)\n"
                "2. Antivirus is scanning the file\n"
                "3. File permissions are restricted\n"
                "Please close any programs using the file and try again."
            )
        raise

