""" Script para capturar imágenes y enviar datos al servidor para detección """

import os
import argparse
import time
from datetime import datetime
import cv2
import requests
from ultralytics import YOLO
import numpy as np


def init_model() -> YOLO:
    """Inicializa el modelo YOLO.

    Returns:
        YOLO: Modelo YOLO inicializado.
    """
    model = YOLO("models/yolov8x.pt")
    return model


def extract_features(image: np.ndarray) -> np.ndarray:
    """Extrae características de la imagen.

    Args:
        image (np.ndarray): Imagen de entrada.

    Returns:
        np.ndarray: Características extraídas.
    """
    # Aquí debes implementar la extracción de características según tu modelo.
    # Ejemplo con un modelo ficticio:
    # features = feature_extractor(image)
    features = image  # Este es un ejemplo; reemplázalo con la extracción real.
    return features


def upload_features(features: np.ndarray, ip_hostname: str) -> None:
    """Envía las características al servidor para la detección.

    Args:
        features (np.ndarray): Características extraídas.
        ip_hostname (str): Dirección IP o nombre del servidor.
    """
    url = f"http://{ip_hostname}/detect"
    _, encoded_img = cv2.imencode(".png", features)
    response = requests.post(url, files={"file": encoded_img.tobytes()}, timeout=120)

    if response.status_code == 200:
        with open("server_detection_result.jpg", "wb") as f:
            f.write(response.content)
        print("Resultado de la detección del servidor guardado.")
    else:
        print("Error al recibir el resultado de la detección.")


def capture_and_process_images(
    model: YOLO,
    output_folder: str,
    total_duration: int,
    interval: int,
    joint_inference: bool,
    server_ip: str,
) -> None:
    """Captura imágenes, extrae características y envía al servidor para detección.

    Args:
        model (YOLO): Modelo YOLO para realizar la predicción.
        output_folder (str): Carpeta donde se guardarán las imágenes.
        total_duration (int): Duración total en segundos para la captura.
        interval (int): Intervalo en segundos entre cada captura de imagen.
        joint_inference (bool): Indica si se debe realizar inferencia conjunta.
        server_ip (str): Dirección IP del servidor.
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

        current_time = time.time()
        elapsed_time_sec = int(current_time - start_time_total)
        curent_elapsed_time = current_time - start_time

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

        if curent_elapsed_time >= interval:
            timestamp = int(time.time() * 1000)
            image_name = f"photo_{timestamp}.png"
            image_path = os.path.join(output_folder, image_name)

            cv2.imwrite(image_path, frame)
            print(f"Foto guardada en: {image_path}")

            if joint_inference:
                features = extract_features(frame)
                upload_features(features, server_ip)
            else:
                result_path = image_prediction(model, image_path)
                upload_image(result_path)
                os.remove(image_path)

            start_time = time.time()

    cap.release()
    print("Finalizando captura de fotos...")


def image_prediction(model: YOLO, image_path: str) -> str:
    """Realiza la predicción en la imagen y guarda el resultado.

    Args:
        image_path (str): Ruta de la imagen de entrada.

    Returns:
        str: Ruta del archivo de resultado.
    """
    results = model(image_path)
    result_path = f"{os.path.splitext(image_path)[0]}_result.jpg"
    results[0].save(result_path)
    return result_path


def upload_image(image_path: str, server_ip: str) -> None:
    """Envía la imagen al servidor y guarda el resultado.

    Args:
        image_path (str): Ruta de la imagen a enviar.
        server_ip (str): Dirección IP del servidor.
    """
    url = f"http://{server_ip}/upload"
    with open(image_path, "rb") as f:
        headers = {"X-File-Name": os.path.basename(image_path)}
        response = requests.post(url, headers=headers, data=f, timeout=120)
        result_image_path = os.path.join(
            "data_server_results",
            f"{os.path.basename(image_path).split('.')[0]}_server_result.jpg",
        )
        with open(result_image_path, "wb") as result_file:
            result_file.write(response.content)
    print(f"Processed image downloaded at: {result_image_path}")


def main():
    """Función principal del script."""
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
        "--server_ip", type=str, required=True, help="Dirección IP del servidor"
    )
    parser.add_argument(
        "--joint_inference",
        type=bool,
        default=False,
        help="Realizar inferencia conjunta",
    )
    args = parser.parse_args()

    if not args.joint_inference:
        print("Inferencia local")
        model = init_model()
    else:
        print("Inferencia conjunta")

    execution_folder = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join("data_collection", execution_folder)
    os.makedirs(output_folder, exist_ok=True)

    capture_and_process_images(
        model,
        output_folder,
        args.total_duration,
        args.interval,
        args.joint_inference,
        args.server_ip,
    )


if __name__ == "__main__":
    main()
