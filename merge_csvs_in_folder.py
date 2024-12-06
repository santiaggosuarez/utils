import os
import pandas as pd

def merge_csvs_in_folder(folder_path, output_file):
    # Lista todos los archivos en la carpeta
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

    if not csv_files:
        print("No se encontraron archivos CSV en la carpeta.")
        return

    # Lista para almacenar los DataFrames
    dataframes = []

    # Leer y almacenar los DataFrames
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        dataframes.append(df)

    # Realizar el merge usando outer join para incluir todas las columnas
    merged_df = pd.concat(dataframes, ignore_index=True, sort=False)

    # Guardar el archivo combinado
    merged_df.to_csv(output_file, index=False)
    print(f"Archivos CSV combinados y guardados en: {output_file}")

# Ruta de la carpeta con los archivos CSV
folder_path = "ruta/a/la/carpeta"  # Cambia esto a tu ruta de carpeta
output_file = "archivo_combinado.csv"  # Cambia esto si necesitas otro nombre

merge_csvs_in_folder(folder_path, output_file)
