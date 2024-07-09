"""
    Dibuja una lista de landmarks y bbox en una imagen y muestra la imagen resultante.
"""
import cv2
import numpy as np

def draw_landmarks(image_path, landmarks=None, bbox=None):
    """
    Dibuja una lista de landmarks y un bounding box en una imagen y muestra la imagen resultante.

    Args:
        image_path (str): La ruta al archivo de imagen.
        landmarks (list): Una lista de puntos (x, y) que representan los landmarks. Default es None.
        bbox (tuple): Coordenadas del bounding box en formato (x, y, width, height). Default es None.
    """
    image = cv2.imread(image_path)
    if image is None:
        print("No se pudo cargar la imagen.")
        return

    if landmarks is not None:
        for (x, y) in landmarks:
            cv2.circle(image, (x, y), 2, (0, 255, 0), -1)

    if bbox is not None:
        x, y, w, h = bbox
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

    cv2.imshow('Landmarks and BBox', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    image_path = "ruta/a/imagen.jpg"
    landmarks = [(30, 50), (35, 55), (40, 60)]  # Ejemplo de coordenadas de landmarks
    bbox = (25, 45, 50, 50)  # Ejemplo de coordenadas del bounding box

    draw_landmarks(image_path, landmarks, bbox)

