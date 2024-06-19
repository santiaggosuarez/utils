"""
  Función para definir si una imagen es NSFW utilizando transformers.
"""

import logging
from PIL import Image
from transformers import pipeline

NSFW_THRESHOLD = 0.9

def is_nsfw_image(image_path):
    """
    Determina si una imagen es NSFW (Not Safe For Work).
    
    Args:
        image_path (str): La ruta al archivo de imagen.
    
    Returns:
        bool: True si la imagen es NSFW, False en caso contrario.
    """
    try:
        img = Image.open(image_path)

        classifier = pipeline("image-classification", model="Falconsai/nsfw_image_detection")
        results = classifier(img)
        
        for result in results:
            if result["label"].lower() == "nsfw" and result["score"] > NSFW_THRESHOLD:
                logging.info(f"The image {image_path} is NSFW")
                return True
        
    except Exception as e:
        logging.error(f"Error analyzing whether it is a NSFW image: {image_path}. Details: {e}")
    
    return False
