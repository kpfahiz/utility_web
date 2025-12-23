import base64
import os

from flask import Blueprint, current_app, render_template, request, send_file
from werkzeug.datastructures import FileStorage

from .document_tools import convert_doc_to_pdf, convert_pdf_to_doc
from .image_tools import SUPPORTED_FORMATS, compress_image, convert_image
from .pdf_tools import (
    compress_pdf,
    extract_pages,
    merge_pdfs,
    rotate_pdf,
    rotate_pdf,
    split_pdf,
    add_signature,
)
from .qr_tools import (
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_FILL_COLOR,
    generate_qr,
)
from .bg_tools import remove_background
from .utils.logger import logger

main = Blueprint("main", __name__)


@main.app_errorhandler(404)
def not_found(error):
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


@main.route("/convert-image", methods=["GET", "POST"])
def convert_image_route() -> str:
    """
    Handle image conversion form and return converted image.
    """
    if request.method == "POST":
        file = request.files.get("image")
        if not file:
            return render_template(
                "convert_image.html",
                converted=False,
                supported_formats=SUPPORTED_FORMATS,
                error="Please select an image file",
            )

        target_format = request.form.get("target_format", "PNG")
        quality = int(request.form.get("quality", 95))

        try:
            result = convert_image(file, target_format, quality)

            # Format file sizes for display
            original_size_mb = result["original_size"] / (1024 * 1024)
            converted_size_mb = result["converted_size"] / (1024 * 1024)
            original_size_kb = result["original_size"] / 1024
            converted_size_kb = result["converted_size"] / 1024

            return render_template(
                "convert_image.html",
                converted=True,
                download_name=result["filename"],
                original_format=result["original_format"],
                target_format=result["target_format"],
                original_size_mb=original_size_mb,
                converted_size_mb=converted_size_mb,
                original_size_kb=original_size_kb,
                converted_size_kb=converted_size_kb,
                supported_formats=SUPPORTED_FORMATS,
            )
        except ValueError as e:
            return render_template(
                "convert_image.html",
                converted=False,
                supported_formats=SUPPORTED_FORMATS,
                error=str(e),
            )
        except Exception as e:
            logger.error(f"Failed to convert image: {e}", exc_info=True)
            return render_template(
                "convert_image.html",
                converted=False,
                supported_formats=SUPPORTED_FORMATS,
                error=f"Conversion failed: {str(e)}",
            )

    return render_template("convert_image.html", converted=False, supported_formats=SUPPORTED_FORMATS)


@main.route("/download/<filename>")
def download(filename: str):
    """
    Download a processed file (image or PDF).
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)
    return send_file(file_path, as_attachment=True)




@main.route("/download-bg-removed/<filename>")
def download_bg_removed(filename: str):
    """
    Download a background removed image.
    Support renaming via query parameter 'name'.
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)
    
    # Check if a custom name is provided
    download_name = request.args.get("name")
    if download_name:
        # Ensure it has the correct extension
        ext = os.path.splitext(filename)[1]
        if not download_name.lower().endswith(ext.lower()):
            download_name += ext
    else:
        download_name = filename

    return send_file(file_path, as_attachment=True, download_name=download_name)


@main.route("/remove-background", methods=["GET", "POST"])
def remove_background_route() -> str:
    """
    Handle background removal form.
    """
    if request.method == "POST":
        file = request.files.get("image")
        if not file:
             return render_template("remove_background.html", error="Please select an image")
        
        background_color = None
        if request.form.get("enable_color") and request.form.get("background_color"):
            background_color = request.form.get("background_color")

        try:
            result = remove_background(file, background_color=background_color)
            
            # Save the result to the upload folder so we can download it
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            save_path = os.path.join(upload_folder, result["filename"])
            
            # Reset stream position before writing
            result["data"].seek(0)
            with open(save_path, "wb") as f:
                f.write(result["data"].read())
            
            # Create data URI for preview
            result["data"].seek(0)
            encoded = base64.b64encode(result["data"].read()).decode("ascii")
            image_data_uri = f"data:{result['mimetype']};base64,{encoded}"
            
            # Format sizes
            original_size_kb = result["original_size"] / 1024
            processed_size_kb = result["processed_size"] / 1024

            return render_template(
                "remove_background.html",
                processed=True,
                image_data_uri=image_data_uri,
                download_name=result["filename"],
                original_size_kb=original_size_kb,
                processed_size_kb=processed_size_kb
            )
            
        except Exception as e:
            logger.error(f"Failed to remove background: {e}", exc_info=True)
            return render_template("remove_background.html", error=f"Error: {str(e)}")

    return render_template("remove_background.html")


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


@main.route("/compress-pdf", methods=["GET", "POST"])
def compress_pdf_route() -> str:
    """
    Handle PDF compression form and return compressed PDF.
    """
    if request.method == "POST":
        file = request.files.get("pdf")
        if not file:
            return render_template("compress_pdf.html", compressed=False, error="Please select a PDF file")

        compression_level = request.form.get("compression_level", "medium")
        result = compress_pdf(file, compression_level)

        # Format file sizes for display
        original_size_mb = result["original_size"] / (1024 * 1024)
        compressed_size_mb = result["compressed_size"] / (1024 * 1024)
        original_size_kb = result["original_size"] / 1024
        compressed_size_kb = result["compressed_size"] / 1024

        return render_template(
            "compress_pdf.html",
            compressed=True,
            download_name=result["filename"],
            original_size_mb=original_size_mb,
            compressed_size_mb=compressed_size_mb,
            original_size_kb=original_size_kb,
            compressed_size_kb=compressed_size_kb,
            compression_percentage=result["compression_percentage"],
        )
    return render_template("compress_pdf.html", compressed=False)



@main.route("/sign-pdf", methods=["GET", "POST"])
def sign_pdf_route() -> str:
    """
    Handle PDF signing form.
    """
    if request.method == "POST":
        pdf_file = request.files.get("pdf")
        image_file = request.files.get("image")
        
        if not pdf_file or not image_file:
             return render_template("sign_pdf.html", error="Please upload both PDF and Image files")
        
        try:
            page_num = int(request.form.get("page_num", 1))
            scale = float(request.form.get("scale", 1.0))
            
            # Interactive Coordinate Mode
            x_ratio = float(request.form.get("x_ratio", 0.0))
            y_ratio = float(request.form.get("y_ratio", 0.0))
            rotation = int(request.form.get("rotation", 0))
            
            # Fallback/Legacy
            position = request.form.get("position", "manual")
            
            result = add_signature(
                pdf_file, 
                image_file, 
                page_num, 
                x_ratio=x_ratio,
                y_ratio=y_ratio,
                scale=scale,
                rotation=rotation,
                position=position
            )
            
            return send_file(result["path"], as_attachment=True, download_name=result["filename"])
            
        except Exception as e:
            logger.error(f"Failed to sign PDF: {e}", exc_info=True)
            return render_template("sign_pdf.html", error=f"Error: {str(e)}")

    return render_template("sign_pdf.html")


@main.route("/edit-pdf", methods=["GET", "POST"])
def edit_pdf_route() -> str:
    """
    Handle PDF editing operations (merge, split, rotate, extract).
    """
    if request.method == "POST":
        operation = request.form.get("operation")

        if operation == "merge":
            files = request.files.getlist("pdfs")
            if len(files) < 2:
                return render_template(
                    "edit_pdf.html",
                    operation=operation,
                    error="Please select at least 2 PDF files to merge"
                )
            result = merge_pdfs(files)
            return render_template(
                "edit_pdf.html",
                operation="merge",
                success=True,
                download_name=result["filename"],
                file_size=result["size"],
            )

        elif operation == "split":
            file = request.files.get("pdf")
            if not file:
                return render_template(
                    "edit_pdf.html",
                    operation=operation,
                    error="Please select a PDF file"
                )
            ranges_str = request.form.get("page_ranges", "")
            # Parse page ranges (e.g., "1-3,4-6,7-10")
            page_ranges = []
            for range_str in ranges_str.split(","):
                range_str = range_str.strip()
                if "-" in range_str:
                    start, end = range_str.split("-", 1)
                    try:
                        page_ranges.append((int(start.strip()), int(end.strip())))
                    except ValueError:
                        return render_template(
                            "edit_pdf.html",
                            operation=operation,
                            error=f"Invalid page range: {range_str}"
                        )

            if not page_ranges:
                return render_template(
                    "edit_pdf.html",
                    operation=operation,
                    error="Please provide page ranges (e.g., 1-3,4-6)"
                )

            result = split_pdf(file, page_ranges)
            return render_template(
                "edit_pdf.html",
                operation="split",
                success=True,
                filenames=result["filenames"],
            )

        elif operation == "rotate":
            file = request.files.get("pdf")
            if not file:
                return render_template(
                    "edit_pdf.html",
                    operation=operation,
                    error="Please select a PDF file"
                )
            rotation = int(request.form.get("rotation", 90))
            page_range = None
            if request.form.get("use_page_range") == "on":
                start = int(request.form.get("start_page", 1))
                end = int(request.form.get("end_page", 1))
                page_range = (start, end)

            result = rotate_pdf(file, rotation, page_range)
            return render_template(
                "edit_pdf.html",
                operation="rotate",
                success=True,
                download_name=result["filename"],
            )

        elif operation == "extract":
            file = request.files.get("pdf")
            if not file:
                return render_template(
                    "edit_pdf.html",
                    operation=operation,
                    error="Please select a PDF file"
                )
            pages_str = request.form.get("pages", "")
            try:
                pages = [int(p.strip()) for p in pages_str.split(",") if p.strip()]
            except ValueError:
                return render_template(
                    "edit_pdf.html",
                    operation=operation,
                    error="Invalid page numbers. Use comma-separated values (e.g., 1,3,5)"
                )

            if not pages:
                return render_template(
                    "edit_pdf.html",
                    operation=operation,
                    error="Please provide page numbers to extract"
                )

            result = extract_pages(file, pages)
            return render_template(
                "edit_pdf.html",
                operation="extract",
                success=True,
                download_name=result["filename"],
            )

    return render_template("edit_pdf.html", operation="")


@main.route("/convert-pdf-doc", methods=["GET", "POST"])
def convert_pdf_doc_route() -> str:
    """
    Handle PDF to DOC conversion.
    """
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return render_template(
                "convert_pdf_doc.html",
                converted=False,
                conversion_type="pdf-to-doc",
                error="Please select a PDF file",
            )

        try:
            result = convert_pdf_to_doc(file)

            # Format file sizes for display
            original_size_mb = result["original_size"] / (1024 * 1024)
            converted_size_mb = result["converted_size"] / (1024 * 1024)
            original_size_kb = result["original_size"] / 1024
            converted_size_kb = result["converted_size"] / 1024

            return render_template(
                "convert_pdf_doc.html",
                converted=True,
                conversion_type="pdf-to-doc",
                download_name=result["filename"],
                original_size_mb=original_size_mb,
                converted_size_mb=converted_size_mb,
                original_size_kb=original_size_kb,
                converted_size_kb=converted_size_kb,
            )
        except ImportError as e:
            return render_template(
                "convert_pdf_doc.html",
                converted=False,
                conversion_type="pdf-to-doc",
                error=f"Library not installed: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Failed to convert PDF to DOC: {e}", exc_info=True)
            return render_template(
                "convert_pdf_doc.html",
                converted=False,
                conversion_type="pdf-to-doc",
                error=f"Conversion failed: {str(e)}",
            )

    return render_template("convert_pdf_doc.html", converted=False, conversion_type="pdf-to-doc")


@main.route("/convert-doc-pdf", methods=["GET", "POST"])
def convert_doc_pdf_route() -> str:
    """
    Handle DOC to PDF conversion.
    """
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return render_template(
                "convert_pdf_doc.html",
                converted=False,
                conversion_type="doc-to-pdf",
                error="Please select a DOC/DOCX file",
            )

        try:
            result = convert_doc_to_pdf(file)

            # Format file sizes for display
            original_size_mb = result["original_size"] / (1024 * 1024)
            converted_size_mb = result["converted_size"] / (1024 * 1024)
            original_size_kb = result["original_size"] / 1024
            converted_size_kb = result["converted_size"] / 1024

            return render_template(
                "convert_pdf_doc.html",
                converted=True,
                conversion_type="doc-to-pdf",
                download_name=result["filename"],
                original_size_mb=original_size_mb,
                converted_size_mb=converted_size_mb,
                original_size_kb=original_size_kb,
                converted_size_kb=converted_size_kb,
            )
        except ImportError as e:
            return render_template(
                "convert_pdf_doc.html",
                converted=False,
                conversion_type="doc-to-pdf",
                error=f"Library not installed: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Failed to convert DOC to PDF: {e}", exc_info=True)
            return render_template(
                "convert_pdf_doc.html",
                converted=False,
                conversion_type="doc-to-pdf",
                error=f"Conversion failed: {str(e)}",
            )

    return render_template("convert_pdf_doc.html", converted=False, conversion_type="doc-to-pdf")