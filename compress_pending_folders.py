"""
 Recibe una ruta principal y busca carpetas 1_real sin comprimir y las comprime. Diviendo estos comprimidos en caso de superar el tamaño máximo y límite de imágenes.
"""
import os, re
import logging
import tarfile
import errno
import select
import sys
import time
import traceback
import shutil

logging.basicConfig(level=logging.INFO)

def compress_to_tar_gz(filename, path_folder):
    """
    Comprime una carpeta en un archivo tar.gz y lo guarda en la carpeta padre de la carpeta comprimida.

    Args:
        filename (str): Nombre del archivo .tar.gz de salida
        path_folder (str): Ruta de la carpeta a comprimir
    """
    logging.info(f"Compressing {filename}...")

    if not filename.endswith(".tar.gz"):
        filename += ".tar.gz"

    output_path = os.path.join(os.path.dirname(path_folder), filename)

    no_space_message_shown = False

    while True:
        try:
            with tarfile.open(output_path, "w:gz") as tar:
                tar.add(path_folder, arcname=os.path.basename(path_folder))
            logging.info(f"{filename} has been compressed!")
            break
        
        except OSError as ose:
            if ose.errno == errno.ENOSPC:
                if not no_space_message_shown:
                    logging.error("No space left on device. Press 'Enter' to finish execution or wait for available space in memory to retry:")
                    no_space_message_shown = True
                    
                rlist, _, _ = select.select([sys.stdin], [], [], 5)
                if rlist:
                    logging.info("Execution finished manually.")
                    return None
            else:
                logging.error(f"OSError: {ose}")
                return None
        
        except Exception as e:
            execution_error = f"{e}\n\n{traceback.format_exc()}"
            logging.error(f"Error compressing {filename}. Details: {execution_error}")
            return None
        
        time.sleep(5)

def split_targz_folder(source_folder, targz_basename, max_size_gb, max_images):
    """
    Divide una carpeta en subpartes menores a un tamaño en GB y opcionalmente a un número máximo de archivos,
    manteniendo los archivos relacionados en las mismas subcarpetas.

    Args:
        source_folder (str): Ruta de la carpeta fuente a dividir.
        targz_basename (str): Nombre base de cada tar.gz a crear.
        max_size_gb (int): Tamaño máximo en GB para cada subparte.
        max_images (int, optional): Número máximo de imágenes en cada tar.gz. Default es None, lo que significa sin límite.
    """
    max_size = float(max_size_gb) * (2**30)
    part = 1
    total_size = sum(os.path.getsize(os.path.join(source_folder, f)) for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f)))
    
    max_images = None if not max_images else int(max_images)
    
    parts_by_size = -(-total_size // max_size)
    parts_by_images = -(-len(os.listdir(source_folder)) // (max_images * 2)) if max_images else parts_by_size
    
    total_parts = int(max(parts_by_size, parts_by_images))
    
    
    if total_parts == 1:
        compress_to_tar_gz(f"{targz_basename}.tar.gz", source_folder)
        return
    elif total_parts == 0:
        return
    

    current_folder_size = 0
    current_file_count = 0
    logging.info(f"Max size {max_size_gb} GB and image limit {max_images}, split into {total_parts} parts.")

    for file_name in sorted(os.listdir(source_folder)):
        file_path = os.path.join(source_folder, file_name)
        if os.path.isfile(file_path):
            related_files = get_related_files(file_name, os.listdir(source_folder))
            total_related_size = sum(os.path.getsize(os.path.join(source_folder, f)) for f in related_files)

            if (current_folder_size + total_related_size > max_size or (max_images is not None and current_file_count + len(related_files) > max_images * 2)):
                part += 1
                current_folder_size = 0
                current_file_count = 0

            dest_folder = os.path.join(os.path.dirname(source_folder), f"{targz_basename}-part_{part}_of_{total_parts}", os.path.basename(source_folder))
            os.makedirs(dest_folder, exist_ok=True)

            for related_file in related_files:
                shutil.move(os.path.join(source_folder, related_file), os.path.join(dest_folder, related_file))

            current_folder_size += total_related_size
            current_file_count += len(related_files)
    
    for i in range(1, part + 1):
        folder_to_compress = os.path.join(os.path.dirname(source_folder), f"{targz_basename}-part_{i}_of_{total_parts}", os.path.basename(source_folder))
        tar_filename = os.path.join(os.path.dirname(source_folder), f"{targz_basename}-part_{i}_of_{part}.tar.gz")
        compress_to_tar_gz(tar_filename, folder_to_compress)

        for file_name in os.listdir(folder_to_compress):
            file_path = os.path.join(folder_to_compress, file_name)
            if os.path.isfile(file_path):
                shutil.move(file_path, os.path.join(source_folder, file_name))
        
        shutil.rmtree(os.path.dirname(folder_to_compress))

def get_related_files(main_file, all_files_in_directory):
    """
    Encuentra y devuelve una lista de archivos relacionados con un archivo principal dado en un directorio.

    Args:
        main_file (str): El nombre del archivo principal para el cual buscar archivos relacionados.
        all_files_in_directory (list of str): Una lista de nombres de archivos presentes en el directorio.

    Returns:
        list of str: Una lista que contiene el archivo principal y todos los archivos relacionados encontrados en el directorio.
    """

    prefix_pattern = re.compile(r'(.+?-origin).*')
    match = prefix_pattern.match(main_file)
    
    if not match:
        return [main_file]
    
    prefix = match.group(1)
    related_files = [file for file in all_files_in_directory if file.startswith(prefix)]
    return related_files

def process_folder(root_path):
    """
    Recorre todas las subcarpetas en busca de una carpeta '1_real' y, si la encuentra,
    aplica el proceso de división y compresión especificado.
    """
    for subdir, dirs, files in os.walk(root_path):
        if '1_real' in dirs:
            full_path = os.path.join(subdir, '1_real')
            logging.info(f"Procesando: {full_path}")
            
            targz_basename = os.path.basename(os.path.dirname(full_path))
            split_targz_folder(full_path, targz_basename, 1, 20000)
            logging.info("-------")


root_path = "/mnt/6a32262d-10d7-4d1f-afd1-e1a2e3db7aed/Descargas/Split/"
process_folder(root_path)
print("Final de la ejecución.")
