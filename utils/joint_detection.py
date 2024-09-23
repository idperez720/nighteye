""" Modulo de funciones """

import os
import requests
import random
import cv2
import numpy as np
from ultralytics import YOLO


def init_model() -> YOLO:
    """Inicializa el modelo YOLO."""
    model = YOLO("models/yolov8x.pt")
    return model


def preprocess_image(image_path: str) -> np.ndarray:
    """Preprocesa la imagen para el modelo y retorna el vector aplanado."""
    image = cv2.imread(image_path)
    # Cambia el tamaño de la imagen a las dimensiones requeridas por el modelo
    resized_image = cv2.resize(
        image, (640, 640)
    )  # Ajusta el tamaño según sea necesario
    # Convierte la imagen a un vector aplanado
    flattened_image = resized_image.flatten()
    return flattened_image, resized_image.shape


def predict_with_model(
    model: YOLO, image_vector: np.ndarray, original_shape: tuple
) -> any:
    """Realiza la predicción con el modelo YOLO a partir del vector aplanado."""
    image = image_vector.reshape(original_shape)

    results = model(image)
    return results


def get_bounding_boxes(results) -> list:
    """Obtiene las coordenadas de las bounding boxes, las etiquetas y
    los porcentajes desde los resultados del modelo."""
    boxes = results[0].boxes
    labels = results[0].names  # Obtiene los nombres de las clases
    bounding_boxes = []
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        label = box.cls[0]  # Obtiene la clase del objeto
        confidence = box.conf[0]  # Obtiene el porcentaje de confianza
        bounding_boxes.append(
            (int(x1), int(y1), int(x2), int(y2), labels[int(label)], confidence)
        )
    return bounding_boxes


def generate_random_color() -> tuple:
    """Genera un color RGB aleatorio."""
    return tuple(random.randint(0, 255) for _ in range(3))


def draw_bounding_boxes(image: np.ndarray, boxes: list) -> np.ndarray:
    """Dibuja las bounding boxes, etiquetas y porcentajes en la imagen original."""
    for box in boxes:
        # Genera un color aleatorio para cada bounding box
        x1 = box["x1"]
        x2 = box["x2"]
        y1 = box["y1"]
        y2 = box["y2"]
        label = box["label"]
        confidence = box["confidence"]
        color = generate_random_color()

        # Dibuja la caja
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        # Preparar el texto
        label_text = f"{label} {confidence:.2f}"

        # Medir el tamaño del texto
        (text_width, text_height), baseline = cv2.getTextSize(
            label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2
        )

        # Definir la posición del texto dentro de la caja
        text_x = x1 + 5  # Espacio desde el borde izquierdo de la caja
        text_y = y1 + text_height + 5  # Espacio desde el borde superior de la caja

        # Ajustar la posición del texto si el fondo del texto se extiende fuera de la caja
        if text_x + text_width > x2:
            text_x = x2 - text_width - 5
        if text_y > y2:
            text_y = y2 - 5

        # Dibujar un rectángulo de fondo para el texto
        cv2.rectangle(
            image,
            (text_x - 3, text_y - text_height - 5),
            (text_x + text_width + 3, text_y + 5),
            color,
            cv2.FILLED,
        )

        # Dibujar el texto
        cv2.putText(
            image,
            label_text,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    return image


def upload_image_preprocesed(
    image_path: str, ip_hostname: list[str] = ["192.168.2.14", "ID-DESKTOP.local"]
) -> str:
    """
    Envía la imagen al servidor y descarga el resultado en la carpeta 'data_server_results'.

    Args:
        image_path (str): Ruta de la imagen a enviar.
    Returns:
        str: Ruta del archivo procesado descargado.
    """
    # Crear la carpeta de resultados si no existe
    result_folder = "data_server_results"
    os.makedirs(result_folder, exist_ok=True)

    url = f"http://{ip_hostname[1]}:8000/"
    prepro_img, img_shape = preprocess_image(image_path)
    # Serializamos el array numpy a una lista para enviarlo como JSON
    prepro_img_serialized = prepro_img.tolist()

    headers = {
        "Content-type": "application/json",
        "X-File-Name": os.path.basename(image_path),
    }

    # Enviamos los datos de la imagen procesada y su shape
    data = {"image_array": prepro_img_serialized, "shape": img_shape}
    response = requests.post(url, headers=headers, json=data, timeout=120)

    # TODO: leer las boxes, dibujarlas y luego guardar la imagen
    if response.status_code == 200:
        # Decodificar la respuesta JSON
        response_data = response.json()

        # Extraer las bounding boxes
        bounding_boxes = response_data.get("bounding_boxes", [])
        original_image = cv2.imread(image_path)
        image_procesed = draw_bounding_boxes(original_image, bounding_boxes)
        result_image_path = os.path.join(
            result_folder,
            f"{os.path.basename(image_path).split('.')[0]}_joint_result.jpg",
        )
        # with open(result_image_path, "wb") as result_file:
        cv2.imwrite(result_image_path, image_procesed)
        print(f"Processed image downloaded at: {result_image_path}")
        return result_image_path
