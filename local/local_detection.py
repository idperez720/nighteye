import cv2
import os
import time
from ultralytics import YOLO
from datetime import datetime
import requests

# Configura el modelo YOLO una vez
model = YOLO("models/yolov8n.pt")


def image_prediction(image_path: str) -> str:
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
) -> None:
    """
    Envía la imagen al PC especificado.

    Args:
        image_path (str): Ruta de la imagen a enviar.
        ip (str): IP del PC receptor.
    """
    url = f"http://{ip_hostname[1]}:8000/"
    with open(image_path, "rb") as f:
        headers = {"X-File-Name": os.path.basename(image_path)}
        response = requests.post(url, headers=headers, data=f)
        print(f"Upload response: {response.text}")


def capture_and_process_images(
    output_folder: str, total_duration: int, interval: int
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
            result_path = image_prediction(image_path)
            upload_image(result_path)
            os.remove(image_path)

            # Reinicia el temporizador
            start_time = time.time()

    # Libera la cámara
    cap.release()
    print("Finalizando captura de fotos...")


def main():
    # Crear una nueva carpeta para cada ejecución
    execution_folder = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join("data_collection", execution_folder)
    os.makedirs(output_folder, exist_ok=True)

    # Configura parámetros
    total_duration = 10
    interval = 2

    # Captura y procesa imágenes
    capture_and_process_images(output_folder, total_duration, interval)


if __name__ == "__main__":
    main()
