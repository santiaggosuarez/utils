import os
import shutil


def extraer_uploading_strings(ruta):
   """
   Función que recibe un archivo y busca si alguna línea comienza con el string "Uploading".
   Si se encuentra, extrae el texto entre "Uploading " y " ..." y lo agrega a un conjunto.
   """
   uploading_set = set()


   with open(ruta, 'r', encoding='utf-8') as archivo:
       for linea in archivo:
           linea = linea.strip()
           if linea.startswith("Uploading ") and "dataset_attachments.info.json" not in linea:
               # Extraer el texto entre "Uploading " y " ..."
               start = len("Uploading ")
               end = linea.find(" ...")
               if end != -1:
                   uploading_text = linea[start:end]
                   uploading_set.add(uploading_text)
  
   print(f"Archivos problematicos: {len(uploading_set)}")
   for i in uploading_set:
       print(i)


   return uploading_set




def mover_archivos_problematicos(ruta_base, rutas_problematicas):
   """
   Busca y mueve archivos problemáticos encontrados en 'rutas_problematicas' dentro de 'ruta_base'
   a una carpeta llamada 'Archivos_problematicos'. También mueve archivos adicionales con extensiones
   .attachments.info.json y .tags.json.
  
   Al finalizar, imprime la cantidad de archivos problemáticos que se movieron.
  
   Parameters:
       ruta_base (str): Ruta base donde buscar y mover los archivos.
       rutas_problematicas (set): Set de rutas relativas de archivos problemáticos a buscar en 'ruta_base'.
   """
   # Crear la carpeta de destino si no existe
   carpeta_destino = os.path.join(ruta_base, "Archivos_problematicos")
  
   archivos_movidos = 0


   for ruta_relativa in rutas_problematicas:
       os.makedirs(carpeta_destino, exist_ok=True)


       # Construir la ruta completa del archivo a buscar
       archivo_a_mover = os.path.join(ruta_base, ruta_relativa)
      
       if os.path.exists(archivo_a_mover):
           # Extraer el nombre base sin extensión
           archivo_base, extension = os.path.splitext(archivo_a_mover)


           # Listado de archivos a mover (con distintas extensiones)
           archivos_a_mover = [
               archivo_a_mover,
               f"{archivo_base}.attachments.info.json",
               f"{archivo_base}.tags.json",
               f"{archivo_base}.numeric_tags.json"
           ]
          
           for archivo in archivos_a_mover:
               if os.path.exists(archivo):
                   # Mover cada archivo a la carpeta de destino
                   shutil.move(archivo, os.path.join(carpeta_destino, os.path.basename(archivo)))
                   archivos_movidos += 1


   print(f"Total de archivos problemáticos movidos: {archivos_movidos}")




def procesar_logs_y_mover_archivos(ruta_general):
   """
   Procesa logs y mueve archivos problematicos. Es necesario tener los logs en la misma ruta general que las carpetas a revisar.
   """
   rutas_problematicas = set()


   # Buscar todos los archivos .log en la ruta general y subcarpetas
   for root, _, files in os.walk(ruta_general):
       for file_name in files:
           if file_name.endswith(".log"):
               log_file_path = os.path.join(root, file_name)
               rutas_problematicas.update(extraer_uploading_strings(log_file_path))


   print(f"Total de rutas problemáticas encontradas: {len(rutas_problematicas)}")


   # Buscar todas las subcarpetas en la ruta general y mover archivos problemáticos en cada una
   for root, dirs, _ in os.walk(ruta_general):
       for dir_name in dirs:
           ruta_subcarpeta = os.path.join(root, dir_name)
           mover_archivos_problematicos(ruta_subcarpeta, rutas_problematicas)


# Ejecucion para multiples rutas en una carpeta general
ruta_general = "/mnt/HDD2/subir/0_Not_Uploaded"
procesar_logs_y_mover_archivos(ruta_general)


"""
# Ejecucion para una ruta y log individual
log_path = ""
source_folder = ""
archivos_problmeaticos = extraer_uploading_strings(log_path)
mover_archivos_problematicos(source_folder, archivos_problmeaticos)
"""


print("Fin.")
