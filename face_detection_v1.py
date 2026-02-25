import logging
import os
import shutil
from argparse import ArgumentParser
import cv2
import dlib
import math
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from utils import setup_logging, download_json

# Actualmente el Roll no es importante para la posición de rostro que se pretende evitar 
HIGH_ROLL_THRESHOLD = 100000
HIGH_YAW_THRESHOLD = 1
HIGH_PITCH_THRESHOLD = 11

MEDIUM_ROLL_THRESHOLD = 100000
MEDIUM_YAW_THRESHOLD = 7
MEDIUM_PITCH_THRESHOLD = 16

LOW_ROLL_THRESHOLD = 100000
LOW_YAW_THRESHOLD = 12
LOW_PITCH_THRESHOLD = 19


def crop_face(image, face):
    """
    Recorta la región del rostro en la imagen original.
    
    Args:
        image (numpy.ndarray): La imagen original.
        face (dlib.rectangle): La bounding box del rostro detectado.
    
    Returns:
        cropped_image (numpy.ndarray): El recorte de la imagen con el rostro.
    """
    left, top, right, bottom = face.left(), face.top(), face.right(), face.bottom()
    cropped_image = image[top:bottom, left:right]
    return cropped_image


def classify_face_level(yaw_angle, pitch_angle):
    """
    Clasifica el nivel de rigurosidad utilizado para definir si un rostro es frontal, a partir de los ángulos de yaw y pitch.

    Args:
        yaw_angle (float): El ángulo yaw de la cara.
        pitch_angle (float): El ángulo pitch de la cara.

    Returns:
        str: El nivel de rigurosidad ("high", "medium", "low").
    """
    yaw_angle = abs(yaw_angle)
    pitch_angle = abs(pitch_angle)
    
    if yaw_angle <= HIGH_YAW_THRESHOLD and pitch_angle <= HIGH_PITCH_THRESHOLD:
        return "high"
    elif yaw_angle <= MEDIUM_YAW_THRESHOLD and pitch_angle <= MEDIUM_PITCH_THRESHOLD:
        return "medium"
    elif yaw_angle <= LOW_YAW_THRESHOLD and pitch_angle <= LOW_PITCH_THRESHOLD:
        return "low"
    else:
        return ""


def get_face_angles(frame, landmarks):
    """
    Calcula los ángulos de rotación, inclinación y giro (roll, pitch y yaw) de un rostro en un fotograma dado, 
    basado en puntos de referencia faciales.

    Args:
        frame (numpy.ndarray): El fotograma de la imagen que contiene el rostro, representado como un array 3D (alto, ancho, canales de color).
        landmarks (list o numpy.ndarray): Una lista o array de 12 elementos que representa 6 puntos de referencia facial.

    Returns:
        roll (int): El ángulo de rotación del rostro.
        pitch (int): El ángulo de inclinación del rostro.
        yaw (int): El ángulo de giro del rostro.
    """
    size = frame.shape

    image_points = np.array([
        (landmarks[4], landmarks[5]),     # Punta de la nariz
        (landmarks[10], landmarks[11]),   # Barbilla
        (landmarks[0], landmarks[1]),     # Esquina izquierda del ojo izquierdo
        (landmarks[2], landmarks[3]),     # Esquina derecha del ojo derecho
        (landmarks[6], landmarks[7]),     # Esquina izquierda de la boca
        (landmarks[8], landmarks[9])      # Esquina derecha de la boca
    ], dtype="double")

    model_points = np.array([
        (0.0, 0.0, 0.0),             # Punta de la nariz
        (0.0, -330.0, -65.0),        # Barbilla
        (-165.0, 170.0, -135.0),     # Esquina izquierda del ojo izquierdo
        (165.0, 170.0, -135.0),      # Esquina derecha del ojo derecho
        (-150.0, -150.0, -125.0),    # Esquina izquierda de la boca
        (150.0, -150.0, -125.0)      # Esquina derecha de la boca
    ])
 
    center = (size[1]/2, size[0]/2)
    focal_length = center[0] / np.tan(60/2 * np.pi / 180)
    camera_matrix = np.array(
                         [[focal_length, 0, center[0]],
                         [0, focal_length, center[1]],
                         [0, 0, 1]], dtype = "double"
                         )

    dist_coeffs = np.zeros((4,1))
    (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

    
    axis = np.float32([[500,0,0], 
                          [0,500,0], 
                          [0,0,500]])
                          
    rvec_matrix = cv2.Rodrigues(rotation_vector)[0]

    proj_matrix = np.hstack((rvec_matrix, translation_vector))
    eulerAngles = cv2.decomposeProjectionMatrix(proj_matrix)[6] 

    pitch, yaw, roll = [math.radians(_.item()) for _ in eulerAngles]


    pitch = math.degrees(math.asin(math.sin(pitch)))
    roll = -math.degrees(math.asin(math.sin(roll)))
    yaw = math.degrees(math.asin(math.sin(yaw)))

    return roll, pitch, yaw


def detect_frontal_face_dlib(image_path, model_path):
    """
    Detecta si hay al menos un rostro frontal en una imagen usando dlib y estimación de pose.
    Se considera un rostro frontal si los ángulos de rotación (roll, pitch, yaw) están dentro
    de ciertos umbrales.

    Args:
        image_path (str): Ruta a la imagen.
        model_path (str): Ruta al modelo de dlib.

    Returns:
        is_frontal (bool): True si se detecta al menos un rostro frontal, False de lo contrario.
        angle_data (dict): Información sobre los ángulos row, pitch y yaw encontrados.
    """
    is_frontal = False
    
    face_detector = dlib.get_frontal_face_detector()
    landmark_predictor = dlib.shape_predictor(model_path)

    image = cv2.imread(image_path)
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detected_faces = face_detector(grayscale_image, 1)
    
    roll_angle, pitch_angle, yaw_angle = "Null", "Null", "Null"

    for face in detected_faces:
        facial_landmarks = landmark_predictor(grayscale_image, face)
        
        if facial_landmarks:
            landmarks = [
                facial_landmarks.part(36).x - face.left(), facial_landmarks.part(36).y - face.top(),  # Ojo izq
                facial_landmarks.part(45).x - face.left(), facial_landmarks.part(45).y - face.top(),  # Ojo der
                facial_landmarks.part(30).x - face.left(), facial_landmarks.part(30).y - face.top(),  # Nariz
                facial_landmarks.part(48).x - face.left(), facial_landmarks.part(48).y - face.top(),  # Boca izq
                facial_landmarks.part(54).x - face.left(), facial_landmarks.part(54).y - face.top(),  # Boca der
                facial_landmarks.part(8).x - face.left(), facial_landmarks.part(8).y - face.top()     # Mentón
            ]

            cropped_face = crop_face(image, face)

            roll_angle, pitch_angle, yaw_angle = get_face_angles(cropped_face, landmarks)

            if abs(roll_angle) < LOW_ROLL_THRESHOLD and abs(pitch_angle) < LOW_PITCH_THRESHOLD and abs(yaw_angle) < LOW_YAW_THRESHOLD:
                is_frontal = True
                break

    angle_data = {
        "image_info": {
            "face_angle_info": {
                "roll": roll_angle,
                "pitch": pitch_angle,
                "yaw": yaw_angle,
                "method": "dlib",
                "threshold levels": {
                    "high":{
                        "roll_threshold": HIGH_ROLL_THRESHOLD,
                        "pitch_threshold": HIGH_PITCH_THRESHOLD,
                        "yaw_threshold": HIGH_YAW_THRESHOLD
                        },
                    "medium":{
                        "roll_threshold": MEDIUM_ROLL_THRESHOLD,
                        "pitch_threshold": MEDIUM_PITCH_THRESHOLD,
                        "yaw_threshold": MEDIUM_YAW_THRESHOLD
                        },
                    "low":{
                        "roll_threshold": LOW_ROLL_THRESHOLD,
                        "pitch_threshold": LOW_PITCH_THRESHOLD,
                        "yaw_threshold": LOW_YAW_THRESHOLD
                        }                    
                    }
            }
        }
    }
    
    if is_frontal:
        angle_data["image_info"]["pre_upload_hp_like_face_level"] = classify_face_level(yaw_angle, pitch_angle)

    return is_frontal, angle_data


def detect_frontal_face_mediapipe(image_path, model_path):
    """
    Detecta si hay un rostro frontal en la imagen usando MediaPipe y estima los ángulos
    de rotación (roll, pitch, yaw). Se considera un rostro frontal si los ángulos están
    dentro de ciertos umbrales.

    Args:
        image_path (str): Ruta a la imagen.
        model_path (str): Ruta al modelo de MediaPipe.

    Returns:
        is_frontal (bool): True si se detecta al menos un rostro frontal, False de lo contrario.
        angle_data (dict): Información sobre los ángulos row, pitch y yaw encontrados.
    """
    is_frontal = False
    
    base_options = python.BaseOptions(model_asset_path=model_path)
    face_landmarker_options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        num_faces=1,
    )
    
    roll_angle, pitch_angle, yaw_angle = "Null", "Null", "Null"

    with vision.FaceLandmarker.create_from_options(face_landmarker_options) as face_landmarker:
        mediapipe_image = mp.Image.create_from_file(image_path)
        face_landmarker_result = face_landmarker.detect(mediapipe_image)

        if face_landmarker_result and face_landmarker_result.face_landmarks:
            facial_landmarks = face_landmarker_result.face_landmarks[0]

            landmarks = [
                facial_landmarks[33].x, facial_landmarks[33].y,   # Esquina izquierda del ojo izquierdo
                facial_landmarks[263].x, facial_landmarks[263].y, # Esquina derecha del ojo derecho
                facial_landmarks[1].x, facial_landmarks[1].y,     # Punta de la nariz
                facial_landmarks[61].x, facial_landmarks[61].y,   # Esquina izquierda de la boca
                facial_landmarks[291].x, facial_landmarks[291].y, # Esquina derecha de la boca
                facial_landmarks[152].x, facial_landmarks[152].y  # Barbilla
            ]

            image = cv2.imread(image_path)
            roll_angle, pitch_angle, yaw_angle = get_face_angles(image, landmarks)

            if abs(roll_angle) < LOW_ROLL_THRESHOLD and abs(pitch_angle) < LOW_PITCH_THRESHOLD and abs(yaw_angle) < LOW_YAW_THRESHOLD:
                is_frontal = True
    
    angle_data = {
        "image_info": {
            "face_angle_info": {
                "roll": roll_angle,
                "pitch": pitch_angle,
                "yaw": yaw_angle,
                "method": "dlib",
                "threshold levels": {
                    "high":{
                        "roll_threshold": HIGH_ROLL_THRESHOLD,
                        "pitch_threshold": HIGH_PITCH_THRESHOLD,
                        "yaw_threshold": HIGH_YAW_THRESHOLD
                        },
                    "medium":{
                        "roll_threshold": MEDIUM_ROLL_THRESHOLD,
                        "pitch_threshold": MEDIUM_PITCH_THRESHOLD,
                        "yaw_threshold": MEDIUM_YAW_THRESHOLD
                        },
                    "low":{
                        "roll_threshold": LOW_ROLL_THRESHOLD,
                        "pitch_threshold": LOW_PITCH_THRESHOLD,
                        "yaw_threshold": LOW_YAW_THRESHOLD
                        }                    
                    }
            }
        }
    }
    
    if pitch_angle != "Null" and yaw_angle != "Null":
        angle_data["image_info"]["pre_upload_hp_like_face_level"] = classify_face_level(yaw_angle, pitch_angle)

    return is_frontal, angle_data


def process_image(image_path, detection_method, model_path):
    """
    Procesa una imagen para detectar si tiene un rostro frontal.
    
    Args:
        image_path (str): Ruta de la imagen.
        detection_method (str): Método de detección a utilizar ('dlib' o 'mediapipe').
        model_path (str): Ruta al modelo a utilizar.

    Returns:
        bool: Indicador de si hay algún rostro frontal y ángulos detectados.
    """
    try:
        if detection_method == "dlib":
            is_frontal, angle_data = detect_frontal_face_dlib(image_path, model_path)
            return is_frontal, angle_data
        elif detection_method == "mediapipe":
            is_frontal, angle_data = detect_frontal_face_mediapipe(image_path, model_path)
            return is_frontal, angle_data
        else:
            logging.info("Método inválido. Use 'dlib' o 'mediapipe'.")
            return None, None
    except Exception as error:
        logging.error(f"Error al procesar la imagen {image_path}: {error}", exc_info=True)
        return None, None


def process_folder(parent_folder_path, detection_method, model_path):
    """
    Procesa una carpeta para detectar y filtrar imágenes con rostros frontales.
    
    Args:
        parent_folder_path (str): Ruta de la carpeta a analizar.
        detection_method (str): Método de detección a utilizar ('dlib' o 'mediapipe').
        model_path (str): Ruta al modelo a utilizar.
    """
    setup_logging("program_logs", f"{os.path.basename(parent_folder_path)}-face_detection")
    image_extensions = (".avif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp")
    
    true_faces_folder = os.path.join(parent_folder_path, "True")
    false_faces_folder = os.path.join(parent_folder_path, "False") 
    
    os.makedirs(true_faces_folder, exist_ok=True)
    os.makedirs(false_faces_folder, exist_ok=True)

    for root_dir, sub_dirs, file_names in os.walk(parent_folder_path):
        for file_name in file_names:
            if file_name.lower().endswith(image_extensions):
                image_file_path = os.path.join(root_dir, file_name)
                
                is_frontal_face, angle_data = process_image(image_file_path, detection_method, model_path)
                
                if is_frontal_face is None:
                    continue

                logging.info(f"{image_file_path} contains frontal face? {is_frontal_face}")

                destination_folder = true_faces_folder if is_frontal_face else false_faces_folder
                shutil.move(image_file_path, os.path.join(destination_folder, file_name))

                json_filename = os.path.splitext(image_file_path)[0] + '.json'
                download_json(angle_data, destination_folder, os.path.basename(json_filename))
                logging.info("-------")


if __name__ == "__main__":
    # Ejecución:
    # python3 src/main/python/crawlers/face_detection.py --method "dlib" --model src/main/resources/shape_predictor_68_face_landmarks_dlib.dat --folder 
    # python3 src/main/python/crawlers/face_detection.py --method "mediapipe" --model src/main/resources/face_landmarker_mediapipe.task --folder 
    
    parser = ArgumentParser(description='Detectar rostros frontales en imágenes.')

    parser.add_argument("--folder", type=str, required=True, help="Ruta a la carpeta que contiene las imágenes")
    parser.add_argument("--model", type=str, required=True, help="Ruta al modelo a utilizar")
    parser.add_argument("--method", type=str, choices=["dlib", "mediapipe"], required=True, help="Método de detección a utilizar ('dlib' o 'mediapipe')")

    args = parser.parse_args()
    
    process_folder(args.folder, args.method, args.model)
    
