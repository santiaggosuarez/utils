"""UTILS GENERALES"""
import tempfile

def guardar_lista_como_txt(lista):
    # Unimos los elementos de la lista con ", " como separador
    contenido = ", ".join(lista)
    
    # Creamos un archivo temporal en modo de escritura
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as archivo_temp:
        archivo_temp.write(contenido)
        print(f"Archivo temporal creado: {archivo_temp.name}")
        
    # El archivo temporal se cierra automáticamente aquí
    return archivo_temp.name

# Ejemplo de uso
mi_lista = ["manzana", "banana", "cereza", "durazno"]
nombre_archivo_temp = guardar_lista_como_txt(mi_lista)
