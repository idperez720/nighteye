"""image_capture.py"""

import os
import time
import cv2
from utils.computer_resources import get_system_usage, ping
from utils.detection import upload_image, upload_image_preprocessed, init_model, image_prediction


def capture_and_process_images(
    output_folder: str, total_duration: int, interval: int, server_ip: str = None
) -> None:
    """
    Captura imágenes desde la cámara, las procesa y las envía a un servidor o las guarda localmente.

    Args:
        output_folder (str): Carpeta donde se guardarán las imágenes.
        total_duration (int): Duración total en segundos para la captura.
        interval (int): Intervalo en segundos entre cada captura de imagen.
        server_ip (str, optional): IP del servidor para la subida de imágenes.
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

        # Calcula el tiempo transcurrido y actualiza el texto en el frame
        elapsed_time_sec = int(time.time() - start_time_total)
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
        if time.time() - start_time >= interval:
            save_and_process_image(frame, output_folder, server_ip)
            start_time = time.time()

    cap.release()
    print("Finalizando captura de fotos...")


def save_and_process_image(frame, output_folder, server_ip):
    """Guarda la imagen, muestra información de recursos y decide el tipo de inferencia."""
    # Guarda la imagen con un nombre basado en el timestamp
    timestamp = int(time.time() * 1000)
    image_name = f"photo_{timestamp}.png"
    image_path = os.path.join(output_folder, image_name)
    cv2.imwrite(image_path, frame)
    print(f"\n*** Foto guardada: {image_path} ***")

    # Obtén el tamaño de la imagen en KB
    image_size = os.path.getsize(image_path) / 1024

    # Obtén el uso de recursos del sistema
    cpu_usage, memory_usage = get_system_usage()
    ping_time = ping(server_ip) if server_ip else None

    # Imprime la información de recursos y tamaño de imagen
    print_resource_info(cpu_usage, memory_usage, image_size, ping_time)

    # Decide el tipo de inferencia
    print("\n*** Decidiendo el tipo de inferencia ***")
    perform_inference(cpu_usage, memory_usage, ping_time, image_path, server_ip)


def print_resource_info(cpu_usage, memory_usage, image_size, ping_time):
    """Imprime información de uso de recursos y ping en formato de tabla."""
    print("\n" + "=" * 50)
    print(f"{'Uso de Recursos':<25} {'Valor':<20}")
    print("=" * 50)
    print(f"{'Uso de CPU (%):':<25} {cpu_usage * 100:.2f}%")
    print(f"{'Uso de Memoria RAM (%):':<25} {memory_usage * 100:.2f}%")
    print(f"{'Tamaño de la imagen (KB):':<25} {image_size:.2f} KB")
    if ping_time is not None:
        print(f"{'Tiempo de ping (ms):':<25} {ping_time:.2f} ms")
    else:
        print(f"{'Tiempo de ping (ms):':<25} {'Error'}")
    print("=" * 50)


def perform_inference(cpu_usage, memory_usage, ping_time, image_path, server_ip):
    """Realiza la inferencia en función de los recursos y el tiempo de ping."""
    if cpu_usage > 0.75 and memory_usage > 0.75:
        if server_ip and ping_time is not None:
            if ping_time < 200:
                print("Inferencia en el servidor")
                upload_image(image_path, server_ip)
            elif ping_time > 500:
                print("Inferencia conjunta")
                upload_image_preprocessed(image_path=image_path, server_ip=server_ip)
            else:
                print("Inferencia local")
                result_data = image_prediction(
                    model=init_model(size='n'), image_path=image_path
                )
                print(f"Resultado guardado en: {result_data['path']}")
    else:
        print("Uso de recursos del sistema muy altos, se recomienda realizar inferencia servidor")
        upload_image(image_path, server_ip)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
