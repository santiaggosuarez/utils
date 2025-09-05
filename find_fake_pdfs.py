import os
from pathlib import Path

def encontrar_falsos_pdfs(directorio):
    """
    Encuentra todos los archivos con extensión .pdf que no son PDFs reales
    """
    falsos_pdfs = []
    
    for archivo in Path(directorio).rglob("*.pdf"):
        if not es_pdf_real(archivo):
            falsos_pdfs.append(str(archivo))
    
    return falsos_pdfs

# Usar así:
falsos = encontrar_falsos_pdfs("/ruta/a/tus/archivos")
for falso in falsos:
    print(f"Archivo falso PDF: {falso}")
