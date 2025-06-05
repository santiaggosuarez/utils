import PyPDF2

def check_pdf_metadata(pdf_path):
    """
    Comprueba si un archivo PDF contiene metadatos y los imprime si están disponibles.
    
    Args:
        pdf_path (str): Ruta del archivo PDF para comprobar los metadatos.
    """
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            metadata = reader.metadata

            if metadata:
                print("The PDF has the following metadata:")
                for key, value in metadata.items():
                    print(f"{key}: {value}")
            else:
                print("The PDF does not have any metadata.")
    except Exception as e:
        print(f"An error occurred: {e}")

check_pdf_metadata("path/to/your/file.pdf")
