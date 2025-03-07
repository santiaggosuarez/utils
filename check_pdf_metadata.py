import PyPDF2

def check_pdf_metadata(pdf_path):
    """
    Checks if a PDF file contains metadata and prints the metadata if available.

    Args:
        pdf_path (str): The path to the PDF file to check for metadata.
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
