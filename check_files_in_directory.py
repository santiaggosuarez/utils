import os
import mimetypes
from PyPDF2 import PdfReader
from PIL import Image

def check_files_in_directory(directory, check_content=False, delete_errors=False):
    """
    Verifica archivos en un directorio y sus subdirectorios, detectando posibles errores.
    
    Args:
        directory (str): Ruta del directorio a escanear
        check_content (bool): Si True, realiza una verificación profunda del contenido
        delete_errors (bool): Si True, elimina los archivos con errores detectados
    
    Returns:
        dict: Estadísticas de los archivos verificados y carpetas abuelas con errores
    """
    stats = {
        'total_files': 0,
        'errors': 0,
        'deleted_files': 0,
        'pdf_files': 0,
        'image_files': 0,
        'other_files': 0,
        'error_details': [],
        'grandparent_folders_with_errors': set()
    }

    # Configurar mimetypes para mayor precisión
    mimetypes.init()
    
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            stats['total_files'] += 1
            
            try:
                # Verificación básica del archivo
                with open(file_path, 'rb') as f:
                    header = f.read(1024)  # Leer cabecera para verificación básica
                    
                    if not header:
                        raise IOError("Archivo vacío o corrupto")
                
                # Detección del tipo de archivo
                mime_type, _ = mimetypes.guess_type(file_path)
                
                # Verificación específica según tipo de archivo
                if mime_type:
                    if mime_type == 'application/pdf':
                        stats['pdf_files'] += 1
                        if check_content:
                            verify_pdf(file_path)
                    elif mime_type.startswith('image/'):
                        stats['image_files'] += 1
                        if check_content:
                            verify_image(file_path)
                    else:
                        stats['other_files'] += 1
                else:
                    stats['other_files'] += 1
                    
            except Exception as e:
                stats['errors'] += 1
                error_info = {
                    'path': file_path,
                    'error': str(e),
                    'type': mime_type if mime_type else 'unknown'
                }
                stats['error_details'].append(error_info)
                
                # Extraer y almacenar la carpeta abuela
                path_parts = os.path.normpath(file_path).split(os.sep)
                if len(path_parts) >= 3:
                    grandparent_folder = path_parts[-3]
                    stats['grandparent_folders_with_errors'].add(grandparent_folder)
                
                print(f"Error en archivo: {file_path}")
                print(f"  Tipo: {mime_type if mime_type else 'Desconocido'}")
                print(f"  Error: {e}")
                
                # Eliminar archivo si se solicita
                if delete_errors:
                    try:
                        os.remove(file_path)
                        stats['deleted_files'] += 1
                        print("  -> Archivo eliminado")
                    except Exception as delete_error:
                        print(f"  -> Error al eliminar archivo: {delete_error}")
                print()
    
    print("\nResumen de verificación:")
    print(f"Total de archivos procesados: {stats['total_files']}")
    print(f"Archivos PDF: {stats['pdf_files']}")
    print(f"Archivos de imagen: {stats['image_files']}")
    print(f"Otros archivos: {stats['other_files']}")
    print(f"Archivos con errores: {stats['errors']}")
    if delete_errors:
        print(f"Archivos eliminados: {stats['deleted_files']}")
    
    # Mostrar carpetas abuelas con errores
    if stats['grandparent_folders_with_errors']:
        print("\nCarpetas abuelas que contienen archivos con errores:")
        for folder in sorted(stats['grandparent_folders_with_errors']):
            print(f" - {folder}")
    
    return stats

def verify_pdf(file_path):
    """Verifica la integridad de un archivo PDF"""
    with open(file_path, 'rb') as f:
        try:
            reader = PdfReader(f)
            if len(reader.pages) == 0:
                raise ValueError("PDF no contiene páginas")
            if not reader.metadata:
                print(f"Advertencia: PDF sin metadatos - {file_path}")
        except Exception as e:
            raise Exception(f"Error en PDF: {str(e)}")

def verify_image(file_path):
    """Verifica la integridad de un archivo de imagen"""
    try:
        with Image.open(file_path) as img:
            img.verify()
            if img.size[0] == 0 or img.size[1] == 0:
                raise ValueError("Dimensiones de imagen inválidas")
    except Exception as e:
        raise Exception(f"Error en imagen: {str(e)}")

# Ejemplo de uso
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Verificador y limpiador de archivos médicos')
    parser.add_argument('ruta', help='Ruta del directorio a verificar')
    parser.add_argument('--check-content', action='store_true', help='Realizar verificación profunda del contenido')
    parser.add_argument('--delete-errors', action='store_true', help='Eliminar archivos con errores detectados')
    args = parser.parse_args()
    
    print(f"Iniciando verificación en: {args.ruta}")
    if args.delete_errors:
        print("MODO ELIMINACIÓN ACTIVADO - Los archivos con errores serán eliminados")
    
    resultados = check_files_in_directory(
        directory=args.ruta,
        check_content=args.check_content,
        delete_errors=args.delete_errors
    )
    
    # Guardar resultados en un archivo
    with open("verificacion_archivos.log", "w") as log_file:
        log_file.write("Resultados de verificación de archivos:\n\n")
        log_file.write(f"Directorio verificado: {args.ruta}\n")
        log_file.write(f"Total archivos: {resultados['total_files']}\n")
        log_file.write(f"Archivos con errores: {resultados['errors']}\n")
        if args.delete_errors:
            log_file.write(f"Archivos eliminados: {resultados['deleted_files']}\n")
        log_file.write("\nDetalles por tipo:\n")
        log_file.write(f"PDF: {resultados['pdf_files']}\n")
        log_file.write(f"Imágenes: {resultados['image_files']}\n")
        log_file.write(f"Otros: {resultados['other_files']}\n\n")
        
        if resultados['errors'] > 0:
            log_file.write("Detalles de errores:\n")
            for error in resultados['error_details']:
                log_file.write(f"Archivo: {error['path']}\n")
                log_file.write(f"Tipo: {error['type']}\n")
                log_file.write(f"Error: {error['error']}\n\n")
            
            log_file.write("\nCarpetas abuelas con archivos erróneos:\n")
            for folder in sorted(resultados['grandparent_folders_with_errors']):
                log_file.write(f" - {folder}\n")
                
"""
Verificación simple:
python3 script.py /ruta/a/verificar

Verificación de contenido:
python3 script.py /ruta/a/verificar --check-content

Eliminar archivos con errores:
python3 script.py /ruta/a/verificar --delete-errors

Combinación de opciones:
python3 check_files_in_directory.py /mnt/HDD2/Medic-app/prospectos_v3 --check-content --delete-errors
"""
