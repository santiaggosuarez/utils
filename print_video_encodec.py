"""
  Imprime todos los codecs de videos encontrados en una ruta dada.
"""
import os
import av

def get_video_codec(file_path):
    """
    Obtiene el códec de codificación de video utilizado en un archivo de video.

    Args:
        file_path (str): Ruta del archivo de video.

    Returns:
        str: Nombre del códec de video utilizado en el archivo de video.
    """
    try:
        with av.open(file_path) as container:
            video_stream = next(s for s in container.streams if s.type == 'video')
            return video_stream.codec_context.codec.name
    except av.AVError as e:
        print(f"Error al procesar el archivo {file_path}: {e}")
        return None

def find_mp4_videos_and_codecs(directory):
    """
    Encuentra todos los archivos MP4 en un directorio y obtiene su códec de video.

    Args:
        directory (str): Ruta del directorio a escanear.

    Returns:
        dict: Diccionario con la ruta del archivo de video como clave y el códec como valor.
    """
    video_codecs = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.mp4'):
                file_path = os.path.join(root, file)
                codec = get_video_codec(file_path)
                if codec:
                    video_codecs[file_path] = codec
    return video_codecs

if __name__ == "__main__":
    # Ruta del directorio a escanear
    directory_path = "/mnt/6a32262d-10d7-4d1f-afd1-e1a2e3db7aed/test_distancias/test1/"
    video_codecs = find_mp4_videos_and_codecs(directory_path)

    for video, codec in video_codecs.items():
        print(f"Video: {video}, Codec: {codec}")
