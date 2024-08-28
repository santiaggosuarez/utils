import cv2
import dlib
import numpy as np

def detect_frontal_face_with_pose(image_path, model_path):
    """
    Detecta si hay al menos un rostro frontal en una imagen usando dlib y estimación de pose.
    Se considera un rostro frontal si los ángulos de rotación (roll, pitch, yaw) están dentro
    de ciertos umbrales.

    Args:
        image_path (str): Ruta a la imagen.
        model_path (str): Ruta al modelo de predicción de landmarks.

    Returns:
        bool: True si se detecta al menos un rostro frontal (dentro de los umbrales de pose), 
              False de lo contrario.
    """
    # **Inicio del código original**
    
    # Cargar el detector de rostros frontal de dlib.
    detector = dlib.get_frontal_face_detector()
    
    # Cargar el predictor de landmarks de dlib.
    predictor = dlib.shape_predictor(model_path)
    
    # Leer la imagen desde el disco.
    image = cv2.imread(image_path)
    
    # Convertir la imagen a escala de grises para mejorar la detección de rostros.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detectar rostros en la imagen.
    faces = detector(gray, 1)
    
    # **Fin del código original**

    # **Inicio del nuevo código (Pose estimation)**
    
    # Puntos 3D del modelo de un rostro genérico, usado para la estimación de la pose.
    model_points = np.array([
        (0.0, 0.0, 0.0),             # Punta de la nariz
        (0.0, -330.0, -65.0),         # Mentón
        (-225.0, 170.0, -135.0),      # Esquina izquierda del ojo izquierdo
        (225.0, 170.0, -135.0),       # Esquina derecha del ojo derecho
        (-150.0, -150.0, -125.0),     # Esquina izquierda de la boca
        (150.0, -150.0, -125.0)       # Esquina derecha de la boca
    ])

    # Parámetros internos de la cámara asumidos (estos pueden variar dependiendo de la cámara usada).
    focal_length = image.shape[1]
    center = (image.shape[1] // 2, image.shape[0] // 2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0, 1]], dtype="double"
    )

    # Iterar sobre los rostros detectados en la imagen.
    for face in faces:
        # Predecir los landmarks faciales para el rostro detectado.
        landmarks = predictor(gray, face)

        # Convertir los landmarks 2D en una matriz numpy.
        image_points = np.array([
            (landmarks.part(30).x, landmarks.part(30).y),  # Punta de la nariz
            (landmarks.part(8).x, landmarks.part(8).y),    # Mentón
            (landmarks.part(36).x, landmarks.part(36).y),  # Esquina izquierda del ojo izquierdo
            (landmarks.part(45).x, landmarks.part(45).y),  # Esquina derecha del ojo derecho
            (landmarks.part(48).x, landmarks.part(48).y),  # Esquina izquierda de la boca
            (landmarks.part(54).x, landmarks.part(54).y)   # Esquina derecha de la boca
        ], dtype="double")

        # Suponemos que no hay distorsión de lente en la imagen.
        dist_coeffs = np.zeros((4, 1))  # Coeficientes de distorsión.

        # Estimar la rotación y traslación del rostro utilizando solvePnP de OpenCV.
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs)

        # Convertir el vector de rotación en una matriz de rotación.
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

        # Convertir la matriz de rotación en ángulos de Euler (Roll, Pitch, Yaw).
        roll, pitch, yaw = rotation_matrix_to_euler_angles(rotation_matrix)

        # Establecer umbrales para los ángulos de rotación (definen lo que consideramos un rostro frontal).
        roll_threshold = 15
        pitch_threshold = 15
        yaw_threshold = 15

        # Si los ángulos están dentro de los umbrales, consideramos que es un rostro frontal.
        if abs(roll) < roll_threshold and abs(pitch) < pitch_threshold and abs(yaw) < yaw_threshold:
            return True

    return False  # Si no se detecta un rostro dentro de los umbrales, retorna False.

def rotation_matrix_to_euler_angles(R):
    """
    Convierte una matriz de rotación en ángulos de Euler (roll, pitch, yaw).

    Args:
        R (numpy.ndarray): Matriz de rotación.

    Returns:
        numpy.ndarray: Ángulos de roll, pitch, yaw en grados.
    """
    # Calcular el seno de y (sy) para determinar si hay singularidad en la rotación.
    sy = np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
    singular = sy < 1e-6

    if not singular:
        # Calcular los ángulos de rotación.
        x = np.arctan2(R[2, 1], R[2, 2])  # Roll
        y = np.arctan2(-R[2, 0], sy)      # Pitch
        z = np.arctan2(R[1, 0], R[0, 0])  # Yaw
    else:
        # En caso de singularidad, simplificamos la estimación de los ángulos.
        x = np.arctan2(-R[1, 2], R[1, 1])
        y = np.arctan2(-R[2, 0], sy)
        z = 0  # Yaw es indeterminado en este caso.

    return np.degrees(np.array([x, y, z]))  # Convertir los ángulos a grados.
