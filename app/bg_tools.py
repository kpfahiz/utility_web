import io
from typing import Optional, Tuple

import numpy as np
from PIL import Image
from rembg import remove

def remove_background(
    file_storage,
    background_color: Optional[str] = None
) -> dict:
    """
    Remove background from an image and optionally replace it with a solid color.
    
    Args:
        file_storage: The uploaded file object (FileStorage).
        background_color: Hex color string (e.g., "#ffffff") or None for transparent.
        
    Returns:
        dict: Contains filename, original_size, processed_size, and the processed image bytes.
    """
    input_image = Image.open(file_storage.stream).convert("RGBA")
    
    # Calculate original size safely
    file_storage.seek(0, 2)  # Seek to end
    original_size = file_storage.tell()
    file_storage.seek(0)  # Reset to beginning
    
    # Remove background
    output_image = remove(input_image)
    
    # If a background color is specified, composite the image
    if background_color:
        # Create a new image with the specified background color
        bg_color_rgb = tuple(int(background_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        # Add alpha channel (255 for opaque)
        bg_image = Image.new("RGBA", output_image.size, bg_color_rgb + (255,))
        
        # Composite the foreground (output_image) onto the background (bg_image)
        # using the alpha channel of the foreground as the mask
        bg_image.paste(output_image, (0, 0), output_image)
        output_image = bg_image.convert("RGB") # Convert back to RGB as alpha is no longer needed if checking compliance? 
        # Actually passport photos might need simple JPEG/PNG. Let's keep RGBA if valid or convert to RGB if requested.
        # Usually passport photos are printed, so RGB/JPEG is fine, but if we want to validly save as PNG with no alpha:
    
    # Save to bytes
    output_io = io.BytesIO()
    # Determine format based on original filename or default to PNG
    filename = file_storage.filename
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'png'
    
    if background_color:
        # if we added a background, we likely want to save as solid.
        # But if the user uploaded a PNG and wants a blue background, we can save as PNG or JPEG.
        # Let's save as PNG for quality.
        output_image.save(output_io, format='PNG')
        output_filename = f"bg_removed_{filename.rsplit('.', 1)[0]}.png"
    else:
        # Transparent background requires PNG
        output_image.save(output_io, format='PNG')
        output_filename = f"bg_removed_{filename.rsplit('.', 1)[0]}.png"
        
    processed_size = output_io.tell()
    output_io.seek(0)
    
    return {
        "filename": output_filename,
        "original_size": original_size,
        "processed_size": processed_size,
        "data": output_io,
        "mimetype": "image/png"
    }
