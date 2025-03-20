"""
Función para recorrer todos los archivos en una ruta dada (incluyendo subcarpetas) e imprimir si hay casos con errores.
"""
import os

def check_files_in_directory(directory):
    error_count = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "rb") as f:
                    f.read(1024)  # Intenta leer una pequeña parte del archivo
            except Exception as e:
                error_count += 1
                print(f"Error en archivo: {file_path}\n  -> {e}")
    
    print(f"Total de archivos con error: {error_count}")

# Ejecución
ruta = "/ruta/a/explorar"
check_files_in_directory(ruta)
