import io
import logging
from PIL import Image

def is_corrupt_image(image_path):
    """
    Verifica si una imagen está corrupta, analizando la misma en tres puntos distintos (principio, mitad y final).

    Args:
        image_path (str): Ruta de la imagen a verificar.

    Returns:
        bool: Booleano que indica si la imagen está corrupta.
    """
    try:
        with open(image_path, "rb") as f:
            img = Image.open(io.BytesIO(f.read()))
            img.load()

        with Image.open(image_path) as img:
            width, height = img.size
            img.crop((0, 0, width, height // 3)).verify()
            img.crop((0, height // 3, width, 2 * height // 3)).verify()
            img.crop((0, 2 * height // 3, width, height)).verify()
            img.load()

        return False
        
    except Exception as e:
        logging.error(f"The image {image_path} is corrupted: {e}", exc_info=True)
        return True
