import os
import qrcode

def generate_qr(data: str) -> str:
    """
    Generator a QR code from the given data.

    Args:
        data: Text or URL to encode.

    Return:
        Path to the generated QR image.
    """

    img = qrcode.make(data)
    output_path = os.path.join("static/uploads", "qr_code.png")
    img.save(output_path)

    return output_path