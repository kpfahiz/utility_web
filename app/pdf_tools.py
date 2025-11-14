import os

from flask import current_app
from pypdf import PdfReader, PdfWriter
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .utils.logger import logger
from .utils.timing import measure_duration


@measure_duration
def compress_pdf(file: FileStorage, compression_level: str = "medium") -> dict:
    """
    Compress a PDF file.

    Args:
        file: Uploaded PDF file.
        compression_level: Compression level ("low", "medium", "high").

    Returns:
        Dictionary containing:
            - filename: Compressed file name
            - path: Absolute path to the compressed PDF
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

        reader = PdfReader(original_path)
        writer = PdfWriter()

        # Copy pages to writer
        for page in reader.pages:
            writer.add_page(page)

        # Write compressed PDF
        # pypdf automatically applies some compression when writing
        # For better compression, we can use different compression levels
        with open(compressed_path, "wb") as output_file:
            writer.write(output_file)

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
        logger.error(f"Failed to compress PDF {filename}: {exc}", exc_info=True)
        raise


@measure_duration
def merge_pdfs(files: list[FileStorage]) -> dict:
    """
    Merge multiple PDF files into one.

    Args:
        files: List of uploaded PDF files.

    Returns:
        Dictionary containing:
            - filename: Merged file name
            - path: Absolute path to the merged PDF
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    merged_filename = "merged_output.pdf"
    merged_path = os.path.join(upload_folder, merged_filename)

    try:
        writer = PdfWriter()

        for file in files:
            filename = secure_filename(file.filename)
            temp_path = os.path.join(upload_folder, filename)
            file.save(temp_path)

            reader = PdfReader(temp_path)
            for page in reader.pages:
                writer.add_page(page)

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

        with open(merged_path, "wb") as output_file:
            writer.write(output_file)

        merged_size = os.path.getsize(merged_path)

        return {
            "filename": merged_filename,
            "path": merged_path,
            "size": merged_size,
        }

    except Exception as exc:
        logger.error(f"Failed to merge PDFs: {exc}", exc_info=True)
        raise


@measure_duration
def split_pdf(file: FileStorage, page_ranges: list[tuple[int, int]]) -> dict:
    """
    Split a PDF into multiple files based on page ranges.

    Args:
        file: Uploaded PDF file.
        page_ranges: List of tuples (start_page, end_page) for each split.

    Returns:
        Dictionary containing:
            - filenames: List of split file names
            - paths: List of paths to split PDFs
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(file.filename)
    original_path = os.path.join(upload_folder, filename)

    try:
        file.save(original_path)
        reader = PdfReader(original_path)

        filenames = []
        paths = []

        for idx, (start, end) in enumerate(page_ranges):
            writer = PdfWriter()
            split_filename = f"split_{idx + 1}_{filename}"
            split_path = os.path.join(upload_folder, split_filename)

            # Ensure valid page range
            start = max(0, min(start - 1, len(reader.pages) - 1))
            end = max(start + 1, min(end, len(reader.pages)))

            for page_num in range(start, end):
                writer.add_page(reader.pages[page_num])

            with open(split_path, "wb") as output_file:
                writer.write(output_file)

            filenames.append(split_filename)
            paths.append(split_path)

        return {
            "filenames": filenames,
            "paths": paths,
        }

    except Exception as exc:
        logger.error(f"Failed to split PDF {filename}: {exc}", exc_info=True)
        raise


@measure_duration
def rotate_pdf(file: FileStorage, rotation: int, page_range: tuple[int, int] | None = None) -> dict:
    """
    Rotate pages in a PDF.

    Args:
        file: Uploaded PDF file.
        rotation: Rotation angle (90, 180, 270).
        page_range: Optional tuple (start_page, end_page) to rotate specific pages.

    Returns:
        Dictionary containing:
            - filename: Rotated file name
            - path: Absolute path to the rotated PDF
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(file.filename)
    original_path = os.path.join(upload_folder, filename)
    rotated_filename = f"rotated_{filename}"
    rotated_path = os.path.join(upload_folder, rotated_filename)

    try:
        file.save(original_path)
        reader = PdfReader(original_path)
        writer = PdfWriter()

        start_page = 0
        end_page = len(reader.pages)

        if page_range:
            start_page = max(0, min(page_range[0] - 1, len(reader.pages) - 1))
            end_page = max(start_page + 1, min(page_range[1], len(reader.pages)))

        for i, page in enumerate(reader.pages):
            if start_page <= i < end_page:
                # Rotate the page before adding to writer
                page.rotate(rotation)
            writer.add_page(page)

        with open(rotated_path, "wb") as output_file:
            writer.write(output_file)

        return {
            "filename": rotated_filename,
            "path": rotated_path,
        }

    except Exception as exc:
        logger.error(f"Failed to rotate PDF {filename}: {exc}", exc_info=True)
        raise


@measure_duration
def extract_pages(file: FileStorage, pages: list[int]) -> dict:
    """
    Extract specific pages from a PDF.

    Args:
        file: Uploaded PDF file.
        pages: List of page numbers to extract (1-indexed).

    Returns:
        Dictionary containing:
            - filename: Extracted file name
            - path: Absolute path to the extracted PDF
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(file.filename)
    original_path = os.path.join(upload_folder, filename)
    extracted_filename = f"extracted_{filename}"
    extracted_path = os.path.join(upload_folder, extracted_filename)

    try:
        file.save(original_path)
        reader = PdfReader(original_path)
        writer = PdfWriter()

        for page_num in pages:
            if 1 <= page_num <= len(reader.pages):
                writer.add_page(reader.pages[page_num - 1])

        with open(extracted_path, "wb") as output_file:
            writer.write(output_file)

        return {
            "filename": extracted_filename,
            "path": extracted_path,
        }

    except Exception as exc:
        logger.error(f"Failed to extract pages from PDF {filename}: {exc}", exc_info=True)
        raise

