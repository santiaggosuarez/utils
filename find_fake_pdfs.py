import os
from pathlib import Path

def find_fake_pdfs(directory):
    """
    Finds all files with a .pdf extension that are not real PDF files
    """
    fake_pdfs = []
    
    for file in Path(directory).rglob("*.pdf"):
        if not is_real_pdf(file):
            fake_pdfs.append(str(file))
    
    return fake_pdfs

fakes = find_fake_pdfs("/path/to/your/files")
for fake in fakes:
    print(f"Fake PDF file: {fake}")
