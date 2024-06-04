"""
  Dada la ruta a una carpeta, cuenta e imprime la cantidad de videos, segundos totales y frames totales encontrados.
"""
import cv2
import os

def calculate_total_video_duration(directory):
  """
    Dada la ruta a una carpeta, cuenta e imprime la cantidad de videos, segundos totales y frames totales encontrados.
  """
    total_seconds = 0
    total_frames = 0
    video_count = 0
    supported_formats = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')  # Añade más formatos si es necesario

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(supported_formats):
                path = os.path.join(root, file)
                cap = cv2.VideoCapture(path)
                if cap.isOpened():
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    duration = frame_count / fps if fps > 0 else 0
                    total_seconds += duration
                    total_frames += frame_count
                    video_count += 1
                cap.release()

    return total_seconds, total_frames, video_count

directory_path = ''
total_duration, total_frames, count = calculate_total_video_duration(directory_path)

print(f"Total Duration: {total_duration} seconds")
print(f"Total Frames: {total_frames}")
print(f"Number of Videos: {count}")
