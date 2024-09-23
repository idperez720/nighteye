""" Script para la detección de objetos en imágenes usando YOLOv8. """

import os
import time
import cv2
from ultralytics import YOLO
from utils.joint_detection import (
    preprocess_image,
    predict_with_model,
    get_bounding_boxes,
    draw_bounding_boxes,
    init_model,
)


SAVE_FOLDER = "C:/Users/ivand/nighteye_server"  # Reemplaza con el directorio de destino


def image_prediction(model: YOLO, image_path: str) -> str:
    """
    Realiza la predicción en la imagen, dibuja las bounding boxes con etiquetas y porcentajes, y guarda el resultado.

    Args:
        image_path (str): Ruta de la imagen de entrada.

    Returns:
        str: Ruta del archivo de resultado.
    """
    # Preprocesar la imagen
    flattened_image, original_shape = preprocess_image(image_path)

    # Realizar la predicción con la imagen preprocesada
    results = predict_with_model(model, flattened_image, original_shape)

    # Obtener las coordenadas de las bounding boxes, las etiquetas y los porcentajes
    boxes = get_bounding_boxes(results)

    # Reconstruir la imagen original para dibujar las bounding boxes
    original_image = cv2.imread(image_path)

    # Dibujar las bounding boxes, etiquetas y porcentajes en la imagen original
    image_with_boxes = draw_bounding_boxes(original_image, boxes)

    # Guardar el resultado
    result_path = f"{image_path.split('.')[0]}_result.jpg"
    cv2.imwrite(result_path, image_with_boxes)

    return result_path


def capture_and_process_images(
    model: YOLO, output_folder: str, total_duration: int, interval: int
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
            image_prediction(model, image_path)
            os.remove(image_path)

            # Reinicia el temporizador
            start_time = time.time()

    # Libera la cámara
    cap.release()
    print("Finalizando captura de fotos...")


def main() -> None:
    """Función principal del script"""
    model = init_model()
    total_duration = 10
    interval = 2

    # Captura y procesa imágenes
    capture_and_process_images(model, SAVE_FOLDER, total_duration, interval)


if __name__ == "__main__":
    main()
