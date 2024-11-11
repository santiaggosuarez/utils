import os
import tarfile


def extract_files(folder_path, extensions):
   """Busca y descomprime archivos con las extensiones especificadas en carpetas y subcarpetas."""
   for root, _, files in os.walk(folder_path):
       for file in files:
           if any(file.endswith(ext) for ext in extensions):
               file_path = os.path.join(root, file)
               try:
                   with tarfile.open(file_path, 'r:*') as tar:
                       print(f"Extracting '{file_path}' in '{root}'...")
                       tar.extractall(path=root)
               except Exception as e:
                   print(f"Error extracting '{file_path}': {e}")


# Usage example
folder_path = "/path/to/folder"
extensions = [".tar", ".tar.gz"]
extract_files(folder_path, extensions)
