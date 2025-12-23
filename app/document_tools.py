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
    Tries to use Microsoft Word (via win32com) for best fidelity.
    Falls back to pdf2docx if Word is not available.

    Args:
        file: Uploaded PDF file.

    Returns:
        Dictionary containing:
            - filename: Converted file name
            - path: Absolute path to the converted DOCX file
            - original_size: Original file size in bytes
            - converted_size: Converted file size in bytes
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(file.filename)
    base_name = os.path.splitext(filename)[0]
    unique_id = uuid.uuid4().hex[:8]
    converted_filename = f"converted_{base_name}_{unique_id}.docx"
    converted_path = os.path.join(upload_folder, converted_filename)
    original_path = os.path.join(upload_folder, f"{unique_id}_{filename}")

    try:
        file.save(original_path)
        original_size = os.path.getsize(original_path)
        
        # Cleanup existing output if any
        if os.path.exists(converted_path):
            try:
                os.remove(converted_path)
            except OSError:
                pass

        conversion_success = False

        # Strategy 1: Microsoft Word Automation (Best Fidelity)
        if os.name == 'nt':  # Windows only
            try:
                import pythoncom
                import win32com.client
                
                # Initialize COM for threading
                pythoncom.CoInitialize()
                
                try:
                    word = win32com.client.Dispatch("Word.Application")
                    word.Visible = False
                    
                    # Open PDF in Word
                    doc = word.Documents.Open(os.path.abspath(original_path), ConfirmConversions=False)
                    
                    # Save as DOCX (wdFormatXMLDocument = 12)
                    doc.SaveAs2(os.path.abspath(converted_path), FileFormat=12)
                    doc.Close()
                    
                    conversion_success = True
                except Exception as e:
                    logger.warning(f"Word automation failed: {e}")
                    # Ensure Word quits if we started it but failed? 
                    # Word might be shared, so be careful. 
                    # Dispatch usually attaches to existing or creates new.
                finally:
                    # We usually want to keep Word open if it was open, but if we launched it...
                    # Dispatch creates a new reference. "Application" object.
                    # Safety: quitting might close user's docs if not careful, but usually acceptable for automation.
                    # Better: try/finally close doc, maybe not quit app depending on environment.
                    # For server, Quit is safer to avoid zombie processes.
                    try:
                         if 'word' in locals():
                             word.Quit()
                    except:
                        pass
                    pythoncom.CoUninitialize()
            except ImportError:
                logger.warning("pywin32 not installed, skipping Word automation.")
            except Exception as e:
                logger.warning(f"Unexpected Word automation error: {e}")

        # Strategy 2: pdf2docx (Fallback)
        if not conversion_success:
            if not PDF2DOCX_AVAILABLE:
                raise ImportError("pdf2docx library not installed and Word conversion failed.")
            
            logger.info("Falling back to pdf2docx")
            try:
                # Use multiprocessing for speedup
                # cpu_count should be standard import
                cv = Converter(original_path)
                cv.convert(converted_path, start=0, end=None, multi_processing=True, cpu_count=4)
                cv.close()
                conversion_success = True
            except Exception as e:
                logger.error(f"pdf2docx failed: {e}")
                raise

        if not conversion_success or not os.path.exists(converted_path):
            raise Exception("Conversion failed to produce output file.")

        converted_size = os.path.getsize(converted_path)

        return {
            "filename": converted_filename,
            "path": converted_path,
            "original_size": original_size,
            "converted_size": converted_size,
        }

    except Exception as exc:
        logger.error(f"Failed to convert PDF to DOCX: {exc}", exc_info=True)
        raise
    finally:
        # Cleanup input file
        if os.path.exists(original_path):
            try:
                os.remove(original_path)
            except:
                pass


@measure_duration
def convert_doc_to_pdf(file: FileStorage) -> dict:
    """
    Convert a DOCX file to PDF format.
    Uses docx2pdf (Word Automation).

    Args:
        file: Uploaded DOCX file.

    Returns:
        Result dictionary.
    """
    if not DOCX2PDF_AVAILABLE:
        raise ImportError("docx2pdf library not installed.")

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(file.filename)
    base_name = os.path.splitext(filename)[0]
    unique_id = uuid.uuid4().hex[:8]
    converted_filename = f"converted_{base_name}_{unique_id}.pdf"
    converted_path = os.path.join(upload_folder, converted_filename)
    original_path = os.path.join(upload_folder, f"{unique_id}_{filename}")

    try:
        file.save(original_path)
        original_size = os.path.getsize(original_path)

        if os.path.exists(converted_path):
             try:
                 os.remove(converted_path)
             except:
                 pass

        # Windows Threading Safety
        if os.name == 'nt':
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except:
                pass
        
        from docx2pdf import convert as d2p_convert
        
        # docx2pdf opens Word.
        d2p_convert(original_path, converted_path)
        
        if os.name == 'nt':
             try:
                 import pythoncom
                 pythoncom.CoUninitialize()
             except:
                 pass

        if not os.path.exists(converted_path):
            raise Exception("Conversion completed but PDF not found.")

        converted_size = os.path.getsize(converted_path)

        return {
            "filename": converted_filename,
            "path": converted_path,
            "original_size": original_size,
            "converted_size": converted_size,
        }

    except Exception as exc:
        logger.error(f"Failed to convert DOCX to PDF: {exc}", exc_info=True)
        msg = str(exc)
        if "Word" in msg or "win32com" in msg:
             raise Exception("Microsoft Word conversion failed. Please ensure Word is installed and not busy.")
        raise
    finally:
        if os.path.exists(original_path):
             try:
                 os.remove(original_path)
             except:
                 pass

