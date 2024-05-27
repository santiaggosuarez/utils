"""
  Recibe una ruta a un archivo csv database de personas famosas y un nombre y arroja si esa persona se encuentra dentro del database.
"""
import csv

def find_person_in_csv(file_path, person_name):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        row_number = 2  
        for row in reader:
            if row['person_name'] == person_name or row['person_standardized_name'] == person_name:
                return row, row_number 
            row_number += 1 
    return "NO PERSON", None

# Uso de la función
file_path = ''
list_person_name = [

]

for person_name in list_person_name:
    row, row_number = find_person_in_csv(file_path, person_name)
    print(row)
    print("La persona se encuentra en la fila N:", row_number)
    print("-------")
