""" image_capture.py """

from datetime import datetime
import os
import time
import cv2
from utils.computer_resources import get_system_usage, ping
from utils.local_detection import upload_image
from utils.joint_detection import upload_image_preprocesed


def capture_and_process_images(
    output_folder: str, total_duration: int, interval: int, server_ip: str = None
) -> None:
    """
    Captura imágenes desde la cámara, las procesa y las envía al PC.

    Args:
        output_folder (str): Carpeta donde se guardarán las imágenes.
        total_duration (int): Duración total en segundos para la captura.
        interval (int): Intervalo en segundos entre cada captura de imagen.
        server_ip (str): IP del servidor para la subida de imágenes.
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
        current_elapsed_time = current_time - start_time

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
        if current_elapsed_time >= interval:
            # Genera un nombre único usando timestamp en milisegundos
            timestamp = int(time.time() * 1000)
            image_name = f"photo_{timestamp}.png"
            image_path = os.path.join(output_folder, image_name)

            # Guarda la imagen en la carpeta de salida
            cv2.imwrite(image_path, frame)
            print(f"\n*** Foto guardada: {image_path} ***")
            
            # Imprimir el tamaño de la imagen
            image_size = os.path.getsize(image_path) / 1024

            # Obtener uso de CPU y memoria
            cpu_usage, memory_usage = get_system_usage()

            # Realizar ping
            ping_time = None
            if server_ip:
                ping_time = ping(server_ip)

            # Imprimir información en formato de tabla
            print("\n" + "="*50)
            print(f"{'Uso de Recursos':<25} {'Valor':<20}")
            print("="*50)
            print(f"{'Uso de CPU (%):':<25} {cpu_usage * 100:.2f}%")
            print(f"{'Uso de Memoria RAM (%):':<25} {memory_usage * 100:.2f}%")
            print(f"{'Tamaño de la imagen (KB):':<25} {image_size:.2f} KB")
            if ping_time is not None:
                print(f"{'Tiempo de ping (ms):':<25} {ping_time:.2f} ms")
            else:
                print(f"{'Tiempo de ping (ms):':<25} {'Error'}")
            print("="*50)

            # Decidir el tipo de inferencia
            print("\n*** Decidiendo el tipo de inferencia ***")
            if cpu_usage < 0.75 and memory_usage < 0.75:
                if server_ip and ping_time is not None:
                    if ping_time < 200:
                        print("Inferencia en el servidor")
                        upload_image(image_path, server_ip)
                    elif ping_time > 500:
                        print("Inferencia conjunta")
                        upload_image_preprocesed(image_path=image_path, server_ip=server_ip)
                    else:
                        print("Inferencia local")
                        upload_image(image_path, server_ip)
            else:
                print("Recursos del sistema muy altos, se recomienda realizar inferencia local")
                upload_image(image_path, server_ip)

            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            # Reinicia el temporizador
            start_time = time.time()
            

    # Libera la cámara
    cap.release()
    print("Finalizando captura de fotos...")