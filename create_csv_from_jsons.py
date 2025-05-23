import os
import json
import csv
from typing import List, Dict


def read_json_from_directory(directory: str) -> List[Dict]:
    """
    Lee todos los archivos JSON desde un directorio especificado y los convierte en una lista de diccionarios.

    Args:
        directory (str): Ruta del directorio que contiene archivos JSON.

    Returns:
        List[Dict]: Lista de diccionarios representando el contenido de los archivos JSON.
    """
    data = []
    json_files_read = 0

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = json.load(file)
                    if isinstance(content, list):
                        data.extend(content)
                    elif isinstance(content, dict):
                        data.append(content)
                    json_files_read += 1
            except json.JSONDecodeError as e:
                print(f"Error al leer {filename}: {e}")

    return data, json_files_read


def write_csv(data: List[Dict], output_path: str) -> int:
    """
    Escribe una lista de diccionarios en un archivo CSV.

    Args:
        data (List[Dict]): Lista de diccionarios a escribir.
        output_path (str): Ruta del archivo CSV de salida.

    Returns:
        int: Número de filas escritas en el archivo CSV.
    """
    if not data:
        print("No hay datos para escribir en el CSV.")
        return 0

    fieldnames = sorted({key for item in data for key in item.keys()})

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    return len(data)


def jsons_to_csv(json_dir: str) -> None:
    """
    Convierte todos los archivos JSON de un directorio en un único archivo CSV.
    El archivo CSV generado se guarda en el mismo directorio, con prefijo "__" para visibilidad.

    Args:
        json_dir (str): Ruta del directorio que contiene los archivos JSON.
    """
    data, num_files = read_json_from_directory(json_dir)
    output_csv_path = os.path.join(json_dir, "__jsons_to_csv.csv")
    num_rows = write_csv(data, output_csv_path)

    print(f"\nResumen:")
    print(f" - Archivos JSON leídos: {num_files}")
    print(f" - Filas escritas en el CSV: {num_rows}")
    print(f" - Archivo generado: {output_csv_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python script.py <directorio_con_jsons>")
    else:
        jsons_to_csv(sys.argv[1])
