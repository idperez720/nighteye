""" Script para capturar imágenes desde la cámara y enviarlas a un PC remoto. """

import os
import time
from datetime import datetime

import cv2
from utils.detection import init_model, image_prediction


def capture_and_process_images(
    model,
    output_folder: str,
    total_duration: int,
    interval: int,
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

            result_data = image_prediction(model, image_path)
            os.remove(result_data["path"])

            # Reinicia el temporizador
            start_time = time.time()

    # Libera la cámara
    cap.release()
    print("Finalizando captura de fotos...")


def main(duracion_total: int = 12, intervalo: int = 3, rpi: bool = True):
    """Función principal del script."""
    model = init_model(size="n", rpi=rpi)
    execution_folder = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join("./data/local/", execution_folder)
    os.makedirs(output_folder, exist_ok=True)

    # Captura y procesa imágenes
    capture_and_process_images(model, output_folder, duracion_total, intervalo)


if __name__ == "__main__":
    main()
