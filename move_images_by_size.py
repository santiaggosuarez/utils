import os
from pathlib import Path
from PIL import Image
import shutil

def move_images_by_size(folder_path: str, size_dict: dict, format_choice: str):
    """
    Mueve imágenes de una carpeta a una subcarpeta según dimensiones mínimas.

    Args:
        folder_path (str): Ruta a la carpeta que contiene las imágenes.
        size_dict (dict): Diccionario con los tamaños mínimos para A3 y A4.
                          Ejemplo: {"a3": {"ancho": 3508, "alto": 4961}, "a4": {"ancho": 2480, "alto": 3508}}
        format_choice (str): "a3" o "a4", según el formato que deseas filtrar.
    """
    # Validar entrada
    if format_choice not in size_dict:
        raise ValueError(f"Formato inválido: {format_choice}. Debe ser 'a3' o 'a4'.")

    # Crear la carpeta de destino
    folder_path = Path(folder_path)
    destination_folder = folder_path / format_choice
    destination_folder.mkdir(exist_ok=True)

    # Obtener las dimensiones mínimas
    min_width = size_dict[format_choice]["ancho"]
    min_height = size_dict[format_choice]["alto"]

    # Extensiones soportadas
    supported_formats = (".avif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp")

    for image_file in folder_path.iterdir():
        if image_file.suffix.lower() in supported_formats:
            try:
                with Image.open(image_file) as img:
                    width, height = img.size
                    # Verificar si cumple con las dimensiones mínimas
                    if width >= min_width and height >= min_height:
                        shutil.move(str(image_file), str(destination_folder / image_file.name))
                        print(f"Movida: {image_file.name} -> {destination_folder}")
            except Exception as e:
                print(f"Error procesando {image_file.name}: {e}")

    print(f"Tareas completadas. Archivos movidos a: {destination_folder}")


if __name__ == "__main__":
    folder = "/ruta/a/tu/carpeta"
    
    size_requirements = {
        "a3": {"ancho": 3508, "alto": 4961},
        "a4": {"ancho": 2480, "alto": 3508},
    }

    format_to_filter = "a3"
    move_images_by_size(folder, size_requirements, format_to_filter)
