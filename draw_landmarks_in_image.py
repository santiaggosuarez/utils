"""
    Dibuja una lista de landmarks en una imagen y muestra la imagen resultante.
"""
import cv2
import numpy as np

def draw_landmarks(image_path, landmarks):
    """
    Dibuja una lista de landmarks en una imagen y muestra la imagen resultante.

    Args:
        image_path (str): La ruta al archivo de imagen.
        landmarks (list): Una lista de puntos (x, y) que representan los landmarks.
    """
    image = cv2.imread(image_path)
    if image is None:
        print("No se pudo cargar la imagen.")
        return

    for (x, y) in landmarks:
        cv2.circle(image, (x, y), 2, (0, 255, 0), -1) 

    cv2.imshow('Landmarks', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":

    image_path = ""
    landmarks = []

    draw_landmarks(image_path, landmarks)
