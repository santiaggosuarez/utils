import os
import json
import pandas as pd

def jsons_to_csv(folder_path):
    """
    Crea un csv a partir de una carpeta con archivos json. Se espera que cada json tenga ciertas keys que se estandarizan a un nuevo nombre.
    """
    csv_filename = os.path.join(folder_path, "jsons_to_csv.csv")
    all_data = []
    unique_others = set()

    column_mapping = {
        "Produce reacciones de fotosensibilidad. el paciente evitará exponerse a la luz solar.": "PHOTOSENSITIVITY_REACTIONS",
        "Medicamento peligroso": "DANGEROUS_MEDICATION",
        "Afecta a la capacidad de conducir": "AFFECTS_DRIVING_ABILITY",
        "source_url": "SOURCE_URL",
        "active_ingredient": "ACTIVE_INGREDIENT",
        "atc": "ATC",
        "pregnancy": "PREGNANCY",
        "lactation": "LACTATION",
        "Mecanismo de acción": "MECHANISM_OF_ACTION",
        "Indicaciones terapéuticas": "THERAPEUTIC_INDICATIONS",
        "Posología": "POSOLOGY",
        "Contraindicaciones": "CONTRAINDICATIONS",
        "Advertencias y precauciones": "WARNINGS_AND_PRECAUTIONS",
        "Insuficiencia hepática": "HEPATIC_IMPAIRMENT",
        "Interacciones": "INTERACTIONS",
        "Embarazo": "PREGNANCY_DETAILS",
        "Lactancia": "LACTATION_DETAILS",
        "Reacciones adversas": "ADVERSE_REACTIONS",
        "Modo de administración": "ADMINISTRATION_METHOD",
        "Insuficiencia renal": "RENAL_IMPAIRMENT",
        "Efectos sobre la capacidad de conducir": "EFFECTS_ON_DRIVING_ABILITY",
        "Sobredosificación": "OVERDOSAGE",
        "Indicaciones terapéuticas y Posología": "THERAPEUTIC_INDICATIONS_AND_POSOLOGY",
        "OBTAINED_DATE": "OBTAINED_DATE"
    }

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "others" in data:
                        unique_others.update(data["others"])
            except Exception as e:
                print(f"Error procesando {filename}: {e}")

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    row = {key: False for key in unique_others}

                    for key, value in data.items():
                        if key == "others":
                            for item in value:
                                row[item] = True
                        else:
                            row[column_mapping.get(key, key.upper())] = value

                    all_data.append(row)
            except Exception as e:
                print(f"Error procesando {filename}: {e}")

    if all_data:
        df = pd.DataFrame(all_data)
        df.rename(columns=column_mapping, inplace=True)
        df.to_csv(csv_filename, index=False, encoding="utf-8")
        print(f"CSV creado con éxito en: {csv_filename}")
    else:
        print("No se encontraron datos válidos para convertir en CSV.")

# === Ejecución ===
folder_path = "carpeta con los archivos json"
jsons_to_csv(folder_path)
