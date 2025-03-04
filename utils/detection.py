""" This module contains the functions to perform the detection of objects in an image. """

import json
import os
import random
from typing import Any, Dict

import cv2
import numpy as np
import requests
from ultralytics import YOLO


def init_model(size: str = "x", rpi: bool = False) -> YOLO:
    """Inicializa y retorna el modelo YOLO."""
    if size == "x":
        print("Using yolov11x model")
        return YOLO("models/yolo11x.pt")
    print("Using yolov11n model")
    model = YOLO("models/yolo11n.pt")
    if rpi:
        if os.path.exists("models/yolo11n_ncnn_model"):
            return YOLO("models/yolo11n_ncnn_model")
        model.export(format="ncnn")
        return YOLO("models/yolo11n_ncnn_model")
    return model


def image_prediction(model: YOLO, image_path: str, image_extension: str) -> Dict[str, Any]:
    """
    Realiza la predicción en la imagen y guarda el resultado.

    Args:
        image_path (str): Ruta de la imagen de entrada.

    Returns:
        str: Ruta del archivo de resultado.
    """
    results = model(image_path)
    speed = results[0].speed
    original_shape = results[0].orig_shape
    boxes = results[0].boxes
    labels = results[0].names
    objects_detected = []
    for box in boxes:
        label = box.cls[0]  # Obtiene la clase del objeto
        confidence = box.conf[0].item()  # Obtiene el porcentaje de confianza
        objects_detected.append((labels[int(label)], confidence))
    result_path = f".{image_path.split('.')[-2]}_result.{image_extension}"
    results[0].save(result_path)
    results_data = {
        "path": result_path,
        "speed": speed,
        "original_shape": original_shape,
        "objects_detected": objects_detected,
    }
    return results_data


def preprocess_image(image_path: str) -> tuple[np.ndarray, tuple]:
    """Lee y preprocesa la imagen, devolviendo un vector aplanado y su forma original."""
    image = cv2.imread(image_path)
    resized_image = cv2.resize(image, (640, 640))
    flattened_image = resized_image.flatten()
    return flattened_image, resized_image.shape


def predict_with_flatten_array(
    model: YOLO, image_vector: np.ndarray, original_shape: tuple
) -> any:
    """Predice con el modelo YOLO usando el vector aplanado de la imagen."""
    image = image_vector.reshape(original_shape)
    return model(image)


def get_bounding_boxes(results) -> list:
    """Extrae las bounding boxes, etiquetas y porcentajes de confianza de los resultados."""
    boxes = results[0].boxes
    labels = results[0].names
    bounding_boxes = []

    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        label = labels[int(box.cls[0])]
        confidence = box.conf[0].item()
        bounding_boxes.append(
            {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "label": label,
                "confidence": confidence,
            }
        )

    return bounding_boxes


def generate_random_color() -> tuple:
    """Genera un color RGB aleatorio."""
    return tuple(random.randint(0, 255) for _ in range(3))


def draw_bounding_boxes(image: np.ndarray, boxes: list) -> np.ndarray:
    """Dibuja las bounding boxes con etiquetas y porcentajes en la imagen."""
    for box in boxes:
        x1, y1, x2, y2 = box["x1"], box["y1"], box["x2"], box["y2"]
        label, confidence = box["label"], box["confidence"]
        color = generate_random_color()

        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        label_text = f"{label} {confidence:.2f}"
        (text_width, text_height), _ = cv2.getTextSize(
            label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2
        )

        text_x = max(x1, min(x2 - text_width, x1 + 5))
        text_y = max(y1 + text_height + 5, min(y2, y1 + 5 + text_height))
        cv2.rectangle(
            image,
            (text_x - 3, text_y - text_height - 5),
            (text_x + text_width + 3, text_y + 5),
            color,
            cv2.FILLED,
        )
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


def upload_image_preprocessed(
    image_path: str, server_ip: str = "ID-DESKTOP.local"
) -> str:
    """Envía la imagen preprocesada al servidor y guarda el resultado."""
    result_folder = "./data/server/"
    os.makedirs(result_folder, exist_ok=True)

    url = f"http://{server_ip}:8000/"
    prepro_img, img_shape = preprocess_image(image_path)
    prepro_img_serialized = prepro_img.tolist()

    headers = {
        "Content-type": "application/json",
        "X-File-Name": os.path.basename(image_path),
    }
    data = {"image_array": prepro_img_serialized, "shape": img_shape}

    response = requests.post(url, headers=headers, json=data, timeout=120)
    if response.status_code == 200:
        response_data = response.json()
        bounding_boxes = response_data.get("bounding_boxes", [])
        result_data = response_data.get("result_data", {})

        original_image = cv2.imread(image_path)
        image_processed = draw_bounding_boxes(original_image, bounding_boxes)
        result_image_path = os.path.join(
            result_folder,
            f"{os.path.splitext(os.path.basename(image_path))[0]}_result.jpg",
        )
        cv2.imwrite(result_image_path, image_processed)

        print(f"Processed image saved at: {result_image_path}")
        result_data["path"] = result_image_path
        return result_data

    raise RuntimeError("Error in server response.")


def upload_image(image_path: str, server_ip: str = None, image_extension: str = "jpg") -> Dict[str, Any]:
    """
    Envía la imagen al servidor y descarga el resultado en la carpeta './data/server/'.

    Args:
        image_path (str): Ruta de la imagen a enviar.
    Returns:
        str: Ruta del archivo procesado descargado.
    """
    # Crear la carpeta de resultados si no existe
    result_folder = "./data/server/"
    os.makedirs(result_folder, exist_ok=True)
    if server_ip is None:
        server_ip = "192.168.2.10"

    headers = {"Content-Type": "image/jpeg", "X-File-Name": "example.jpg"}
    url = f"http://{server_ip}:8000/"
    with open(image_path, "rb") as f:
        response = requests.post(url, headers=headers, data=f, timeout=120)

        if response.status_code == 200:
            boundary = response.headers["Content-Type"].split("boundary=")[1]
            parts = response.content.split(f"--{boundary}".encode())
            json_part = parts[1].split(b"\r\n\r\n")[1]
            image_part = parts[2].split(b"\r\n\r\n")[1][:-2]

            # Process JSON
            result_data = json.loads(json_part)
            # Save image

            result_image_path = os.path.join(
                result_folder,
                f"{os.path.basename(image_path).split('.')[0]}_server_result.{image_extension}",
            )
            with open(result_image_path, "wb") as result_file:
                result_file.write(image_part)

            print(f"Processed image downloaded at: {result_image_path}")
            return result_data
        raise RuntimeError("Error in server response.")
