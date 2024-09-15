"""Script de detección en el servidor"""

import os
import time
import cv2
from ultralytics import YOLO

SAVE_FOLDER = "C:/Users/ivand/nighteye_server"  # Reemplaza con el directorio de destino
os.makedirs(SAVE_FOLDER, exist_ok=True)  # Asegura que la carpeta de destino exista


def init_model() -> YOLO:
    """Inicializa el modelo YOLO.

    Returns:
        YOLO: Modelo YOLO inicializado.
    """
    model = YOLO("models/yolov8x.pt")
    return model


def image_prediction(model: YOLO, image_path: str) -> str:
    """
    Realiza la predicción en la imagen y guarda el resultado.

    Args:
        image_path (str): Ruta de la imagen de entrada.

    Returns:
        str: Ruta del archivo de resultado.
    """
    results = model(image_path)
    result_path = f"{os.path.splitext(image_path)[0]}_result.jpg"
    results[0].save(result_path)
    return result_path


def capture_and_process_images(
    model: YOLO, output_folder: str, total_duration: int, interval: int
) -> None:
    """
    Captura imágenes desde la cámara, las procesa y las guarda.

    Args:
        model (YOLO): Modelo YOLO para realizar la predicción.
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

            # Procesa la imagen y elimina el archivo original
            result_path = image_prediction(model, image_path)
            os.remove(image_path)
            print(f"Imagen procesada guardada en: {result_path}")

            # Reinicia el temporizador
            start_time = time.time()

    # Libera la cámara
    cap.release()
    print("Finalizando captura de fotos...")


def main() -> None:
    """Función principal del script"""
    model = init_model()
    total_duration = 10  # Duración total de captura en segundos
    interval = 2  # Intervalo entre capturas en segundos

    # Captura y procesa imágenes
    capture_and_process_images(model, SAVE_FOLDER, total_duration, interval)


if __name__ == "__main__":
    main()
