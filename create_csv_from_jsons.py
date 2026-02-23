"""
# Procesar carpeta específica
python script.py /ruta/a/mis/jsonl

# Procesar carpeta actual
python script.py .
"""

import json
import pandas as pd
import os
import argparse
from pathlib import Path

def jsonl_to_csv(jsonl_file_path):
    """
    Convierte un archivo JSONL a CSV
    """
    try:
        data = []
        with open(jsonl_file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    json_obj = json.loads(line)
                    data.append(json_obj)
                except json.JSONDecodeError as e:
                    print(f"    ⚠️  Error JSON línea {line_num}: {e}")
                    continue
        
        if not data:
            print(f"    ⚠️  Archivo vacío: {jsonl_file_path.name}")
            return False
        
        df = pd.DataFrame(data)
        output_file = jsonl_file_path.with_suffix('.csv')
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"    ✅ Convertido: {len(data)} filas → {output_file.name}")
        return True
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def process_folder(folder_path):
    """
    Procesa todos los archivos JSONL en una carpeta y subcarpetas
    """
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"❌ La carpeta '{folder_path}' no existe")
        return
    
    print(f"🔍 Buscando archivos JSONL en: {folder_path}")
    print("📂 Incluyendo subcarpetas...")
    print("-" * 60)
    
    stats = {
        'total_folders': 0,
        'jsonl_files': 0,
        'successful_conversions': 0,
        'failed_conversions': 0
    }
    
    jsonl_extensions = ['.jsonl', '.jsonlines', '.jl']
    
    for root, dirs, files in os.walk(folder_path):
        stats['total_folders'] += 1
        current_folder = Path(root)
        
        for file in files:
            file_path = current_folder / file
            
            # Verificar si es archivo JSONL
            if file_path.suffix.lower() in jsonl_extensions:
                stats['jsonl_files'] += 1
                print(f"📄 Procesando: {file_path.relative_to(folder_path)}")
                
                success = jsonl_to_csv(file_path)
                
                if success:
                    stats['successful_conversions'] += 1
                else:
                    stats['failed_conversions'] += 1
    
    print("=" * 60)
    print("📊 ESTADÍSTICAS FINALES")
    print("=" * 60)
    print(f"📂 Carpetas procesadas: {stats['total_folders']}")
    print(f"📄 Archivos JSONL encontrados: {stats['jsonl_files']}")
    print(f"✅ Conversiones exitosas: {stats['successful_conversions']}")
    print(f"❌ Conversiones fallidas: {stats['failed_conversions']}")
    
    if stats['jsonl_files'] > 0:
        success_rate = (stats['successful_conversions'] / stats['jsonl_files']) * 100
        print(f"📊 Tasa de éxito: {success_rate:.1f}%")
        
        if stats['successful_conversions'] > 0:
            print(f"💾 Archivos CSV generados en: {folder_path}")

def main():
    parser = argparse.ArgumentParser(
        description='Convertir todos los archivos JSONL a CSV en una carpeta y subcarpetas'
    )
    parser.add_argument('folder', help='Ruta de la carpeta con archivos JSONL')
    
    args = parser.parse_args()
    
    process_folder(args.folder)

if __name__ == "__main__":
    main()
