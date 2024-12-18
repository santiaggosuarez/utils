import os
import pandas as pd

def merge_csvs_in_folder(folder_path, output_file):
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

    if not csv_files:
        print("No se encontraron archivos CSV en la carpeta.")
        return

    dataframes = []

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        dataframes.append(df)

    merged_df = pd.concat(dataframes, ignore_index=True, sort=False)

    merged_df.to_csv(output_file, index=False)
    print(f"Archivos CSV combinados y guardados en: {output_file}")

folder_path = "ruta/a/la/carpeta"
output_file = "archivo_combinado.csv" 

merge_csvs_in_folder(folder_path, output_file)
