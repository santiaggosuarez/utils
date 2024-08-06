import pandas as pd
import os


def add_total_column_and_sort(first_csv_path, second_csv_path):
   first_df = pd.read_csv(first_csv_path)
   second_df = pd.read_csv(second_csv_path)
  
   first_df = first_df.rename(columns={'likely_face_id': 'id'})
  
   first_df['id'] = first_df['id'].astype(str)
   second_df['id'] = second_df['id'].astype(str)
  
   merged_df = second_df.merge(first_df[['id', 'total']], on='id', how='left')
  
   merged_df['total'] = merged_df['total'].fillna(0)
  
   merged_df = merged_df.sort_values(by='total')
  
   second_csv_dir = os.path.dirname(second_csv_path)
   second_csv_name = os.path.basename(second_csv_path)
   second_csv_name_no_ext, ext = os.path.splitext(second_csv_name)
   output_csv_name = f"{second_csv_name_no_ext}-SORT{ext}"
   output_csv_path = os.path.join(second_csv_dir, output_csv_name)
  
   merged_df.to_csv(output_csv_path, index=False)
  
   print(f"Archivo guardado en: {output_csv_path}")


# Ejecución
people_log_csv = 'Registro de personas crawleadas_ real-identified - SS - real-identified.csv'
people_csv = 'people_database_v18.csv'


add_total_column_and_sort(people_log_csv, people_csv)
