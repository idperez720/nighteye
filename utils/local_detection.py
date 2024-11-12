""" This module contains the functions to perform local detection using YOLOv8. """

import os
from typing import Any, Dict
import requests
from ultralytics import YOLO


def init_model() -> YOLO:
    """Inicializa el modelo YOLO y lo exporta a NCNN.

    Returns:
        YOLO: Modelo YOLO inicializado.
    """
    model = YOLO("models/yolov8n.pt")
    model.export(format="ncnn")
    ncnn_model = YOLO("models/yolov8n_ncnn_model")
    return ncnn_model


def upload_image(image_path: str, server_ip: str = None) -> str:
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
    if server_ip is None:
        server_ip = "ID-DESKTOP.local"

    url = f"http://{server_ip}:8000/"
    with open(image_path, "rb") as f:
        headers = {
            "X-File-Name": os.path.basename(image_path),
            "Content-type": "image/jpeg",
        }
        response = requests.post(url, headers=headers, data=f, timeout=120)

        # Guardar la imagen procesada en 'data_server_results'
        result_image_path = os.path.join(
            result_folder,
            f"{os.path.basename(image_path).split('.')[0]}_server_result.jpg",
        )
        with open(result_image_path, "wb") as result_file:
            result_file.write(response.content)

    print(f"Processed image downloaded at: {result_image_path}")
    return result_image_path


def image_prediction(model: YOLO, image_path: str) -> Dict[str, Any]:
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
    result_path = f".{image_path.split('.')[-2]}_result.jpg"
    results[0].save(result_path)
    results_data = {
        "path": result_path,
        "speed": speed,
        "original_shape": original_shape,
        "objects_detected": objects_detected,
    }
    return results_data
