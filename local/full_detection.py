""" Script para capturar imágenes desde la cámara y enviarlas a un PC remoto. """

import os
import argparse
import time
from datetime import datetime

import cv2
import requests
import numpy as np
from ultralytics import YOLO


def init_model() -> YOLO:
    """Inicializa el modelo YOLO y lo exporta a NCNN.

    Returns:
        YOLO: Modelo YOLO exportado a NCNN.
    """
    model = YOLO("models/yolov8n.pt")
    model.export(format="ncnn")
    ncnn_model = YOLO("models/yolov8n_ncnn_model")
    return ncnn_model


def extract_features(image_path: str) -> np.ndarray:
    """Extrae características de la imagen utilizando un modelo pre-entrenado.

    Args:
        image_path (str): Ruta de la imagen.

    Returns:
        np.ndarray: Características extraídas.
    """
    # Aquí podrías usar un modelo preentrenado para extraer características.
    # Por simplicidad, supongamos que se obtiene una representación de la imagen.
    image = cv2.imread(image_path)
    resized_image = cv2.resize(image, (640, 640))  # Redimensiona si es necesario
    features = resized_image.flatten()  # Ejemplo simple de características
    return features


def upload_features(
    image_path: str, ip_hostname: list[str] = ["192.168.2.14", "ID-DESKTOP.local"]
) -> dict:
    """Envía las características de la imagen al servidor y recibe la detección.

    Args:
        image_path (str): Ruta de la imagen.
        server_url (str): URL del servidor.

    Returns:
        dict: Resultado de la detección.
    """

    url = f"http://{ip_hostname[1]}:8000/"
    features = extract_features(image_path)
    features_bytes = features.tobytes()

    response = requests.post(
        url,
        files={"file": (os.path.basename(image_path), features_bytes)},
        timeout=120,
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al enviar características: {response.status_code}")
        return {}


def draw_bounding_boxes(image_path: str, detections: dict) -> None:
    """Dibuja las Bounding Boxes en la imagen según las detecciones recibidas.

    Args:
        image_path (str): Ruta de la imagen.
        detections (dict): Detecciones recibidas del servidor.
    """
    image = cv2.imread(image_path)
    for detection in detections.get("boxes", []):
        x1, y1, x2, y2 = detection["bbox"]
        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

    result_path = image_path
    cv2.imwrite(result_path, image)
    print(f"Imagen con Bounding Boxes guardada en: {result_path}")


def image_prediction(model: YOLO, image_path: str) -> str:
    """
    Realiza la predicción en la imagen y guarda el resultado.

    Args:
        image_path (str): Ruta de la imagen de entrada.

    Returns:
        str: Ruta del archivo de resultado.
    """
    results = model(image_path)
    result_path = f"{image_path.split('.')[0]}_result.jpg"
    results[0].save(result_path)
    return result_path


def upload_image(
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
    with open(image_path, "rb") as f:
        headers = {"X-File-Name": os.path.basename(image_path)}
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


def capture_and_process_images(
    model,
    output_folder: str,
    total_duration: int,
    interval: int,
    type_inference: str,
) -> None:
    """
    Captura imágenes desde la cámara, las procesa y las envía al PC.

    Args:
        output_folder (str): Carpeta donde se guardarán las imágenes.
        total_duration (int): Duración total en segundos para la captura.
        interval (int): Intervalo en segundos entre cada captura de imagen.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se puede abrir la cámara")
        return

    start_time_total = time.time()
    start_time = start_time_total

    while time.time() - start_time_total < total_duration:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se puede recibir frame (finalizando...)")
            break

        # Calcula el tiempo transcurrido y el tiempo actual
        current_time = time.time()
        elapsed_time_sec = int(current_time - start_time_total)
        curent_elapsed_time = current_time - start_time

        # Agrega el tiempo transcurrido al frame
        cv2.putText(
            frame,
            f"Tiempo transcurrido: {elapsed_time_sec}s",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        # Verifica si ha pasado el intervalo
        if curent_elapsed_time >= interval:
            # Genera un nombre único usando timestamp en milisegundos
            timestamp = int(time.time() * 1000)
            image_name = f"photo_{timestamp}.png"
            image_path = os.path.join(output_folder, image_name)

            # Guarda la imagen en la carpeta de salida
            cv2.imwrite(image_path, frame)
            print(f"Foto guardada en: {image_path}")

            # Procesa la imagen y la sube

            if type_inference == "local":
                image_prediction(model, image_path)
                os.remove(image_path)
            elif type_inference == "server":
                upload_image(image_path)
            elif type_inference == "joint":
                detections = upload_features(image_path)
                draw_bounding_boxes(image_path, detections)

            # Reinicia el temporizador
            start_time = time.time()

    # Libera la cámara
    cap.release()
    print("Finalizando captura de fotos...")


def main():
    """Función principal del script."""
    # Crear una nueva carpeta para cada ejecución
    # Configuración de argparse para recibir parámetros
    parser = argparse.ArgumentParser(description="Captura y procesa imágenes.")
    parser.add_argument(
        "--total_duration",
        type=int,
        default=10,
        help="Duración total de la captura en segundos",
    )
    parser.add_argument(
        "--interval", type=int, default=2, help="Intervalo entre capturas en segundos"
    )
    parser.add_argument(
        "--type_inference",
        type=str,
        default="local",
        help="Realizar inferencia en el servidor",
    )
    args = parser.parse_args()

    # Crear una nueva carpeta para cada ejecución
    if args.type_inference == "local":
        print("Inferencia local")
        model = init_model()
    elif args.type_inference == "server":
        print("Inferencia en el servidor")
        model = None
    elif args.type_inference == "joint":
        print("Inferencia en conjunta")
        model = None
    else:
        print("Tipo de inferencia no válido: local, server, joint")
        return None
    execution_folder = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join("data_local_results", execution_folder)
    os.makedirs(output_folder, exist_ok=True)

    # Captura y procesa imágenes
    capture_and_process_images(
        model, output_folder, args.total_duration, args.interval, args.type_inference
    )


if __name__ == "__main__":
    main()
