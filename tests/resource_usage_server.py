"""This module contains functions to run detection tests, capturing images at intervals
for a set duration and logging resource usage.
"""

import os
import time
from utils.detection import upload_image
from utils.computer_resources import measure_resources_during_prediction, store_results
from utils.image_capture import initialize_camera, capture_and_save_image

"""
def run_detection_tests(
    capture_interval_seconds: int = 3,
    output_folder: str = "./data/local/",
    output_csv: str = "./data/tests/",
    server_ip: str = None,
    image_ext: str = None
) -> None:
    '''Runs detection tests, capturing images at intervals for a set duration and logging
    resource usage.

    Args:
        capture_interval_seconds (int): Interval between captures in seconds.
        output_folder (str): Folder where the images will be saved.
        output_csv (str): Path to the output CSV file.
    '''
    # Initialize camera and model
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_csv, exist_ok=True)
    os.makedirs("./data/local/smoke_capture", exist_ok=True)

    try:
        cap = initialize_camera()
    except RuntimeError as e:
        print(e)
        return

    start_time = time.time()
    photo_count = 0

    
    
    photo_paths = [
        f
        for f in os.listdir(output_folder)
        if os.path.isfile(os.path.join(output_folder, f))  # Check if it's a file
        and f.lower().endswith((".jpg", ".jpeg", ".png", ".tiff", ".tif"))  # Check if it's an image
        and "result" not in f.lower()  # Exclude files with 'result' in their name
    ]

    '''
    while True:
        timestamp = int(time.time() * 1000)
        image_name = f"photo_{timestamp}.{image_ext}"
        image_path = os.path.join(output_folder, image_name)

        try:
            capture_and_save_image(cap, image_path, image_ext)
        except (IOError, RuntimeError) as e:
            print(f"Failed to capture image: {e}")
            continue

        photo_count += 1

        try:
            start_processing_time = time.time()
            avg_cpu_usage, avg_memory_usage, results_data = measure_resources_during_prediction(
                lambda: upload_image(image_path=image_path, server_ip=server_ip, image_extension=image_ext)
            )
            processing_time = time.time() - start_processing_time

            store_results(
                f"{output_csv}resource_usage_server_{int(start_time * 1000)}.csv",
                image_size=os.path.getsize(image_path),
                processing_time=processing_time,
                cpu_usage=avg_cpu_usage,
                memory_usage=avg_memory_usage,
                results_data=results_data,
                detection_place="server",
            )

            print(
                f"Capture {photo_count} at {time.strftime('%H:%M:%S')}, "
                f"CPU: {avg_cpu_usage*100:.2f}%, Memory: {avg_memory_usage*100:.2f}%"
            )
            print("=" * 50)

        except Exception as e:
            print(f"[ERROR] Error procesando imagen: {e}")

        time.sleep(capture_interval_seconds)'''











    for photo in photo_paths:

        image_path = os.path.join("./data/local/smoke_capture/", photo)
        try:
            capture_and_save_image(cap, image_path, image_ext) # Capture and save using desire image format
        except (IOError, RuntimeError) as e:
            print(f"Failed to capture image: {e}")
            continue

        image_path = os.path.join(output_folder, photo)
        photo_count += 1

        # Measure resource usage during image prediction
        start_processing_time = time.time()
        avg_cpu_usage, avg_memory_usage, results_data = (
            measure_resources_during_prediction(
                lambda image_path=image_path: upload_image(
                    image_path=image_path, server_ip=server_ip
                )
            )
        )
        processing_time = time.time() - start_processing_time
        # Store the results in the CSV file
        store_results(
            f"{output_csv}resource_usage_server_{int(start_time * 1000)}.csv",
            image_size=os.path.getsize(image_path),
            processing_time=processing_time,
            cpu_usage=avg_cpu_usage,
            memory_usage=avg_memory_usage,
            results_data=results_data,
            detection_place="server",
        )

        # Log resource usage
        print(
            f"Capture {photo_count} at {time.strftime('%H:%M:%S')}, "
            f"CPU: {avg_cpu_usage*100:.2f}%, Memory: {avg_memory_usage*100:.2f}%"
        )
        print("=" * 50)

        # Wait for the next capture
        time.sleep(capture_interval_seconds)

    print(f"Detection test completed. Total photos taken: {photo_count}")
    print(f"Data saved to {output_csv}")


"""


def run_detection_tests(
    capture_interval_seconds: int = 3,
    output_folder: str = "./data/local/",
    output_csv: str = "./data/tests/",
    server_ip: str = None,
    image_ext: str = "jpg"
) -> None:
    """Captura imágenes periódicamente, las envía al servidor, mide el uso de recursos
    y guarda los resultados.

    Args:
        capture_interval_seconds (int): Intervalo entre capturas en segundos.
        output_folder (str): Carpeta donde se guardan las imágenes.
        output_csv (str): Carpeta donde se guarda el CSV de resultados.
        server_ip (str): IP del servidor al que se envían las imágenes.
        image_ext (str): Formato de imagen (ej: 'jpg', 'png').
    """
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_csv, exist_ok=True)

    try:
        cap = initialize_camera()
    except RuntimeError as e:
        print(f"[ERROR] No se pudo inicializar la cámara: {e}")
        return

    start_time = time.time()
    photo_count = 0

    while True:
        try:
            # Captura imagen y obtiene la ruta directamente
            image_path = capture_and_save_image(cap, output_folder, image_ext)

            if not os.path.exists(image_path):
                print(f"[ERROR] Imagen no encontrada tras captura: {image_path}")
                continue

            photo_count += 1

            # Medir recursos durante la predicción
            start_processing_time = time.time()
            avg_cpu_usage, avg_memory_usage, results_data = measure_resources_during_prediction(
                lambda image_path=image_path: upload_image(
                    image_path=image_path,
                    server_ip=server_ip,
                    image_extension=image_ext
                )
            )
            processing_time = time.time() - start_processing_time

            # Guardar resultados en CSV
            store_results(
                f"{output_csv}/resource_usage_server_{int(start_time * 1000)}.csv",
                image_size=os.path.getsize(image_path),
                processing_time=processing_time,
                cpu_usage=avg_cpu_usage,
                memory_usage=avg_memory_usage,
                results_data=results_data,
                detection_place="server",
            )

            # Log de recursos
            print(
                f"Capture {photo_count} at {time.strftime('%H:%M:%S')}, "
                f"CPU: {avg_cpu_usage*100:.2f}%, Memory: {avg_memory_usage*100:.2f}%"
            )
            print("=" * 50)

        except Exception as e:
            print(f"[ERROR] Error procesando imagen: {e}")

        # Esperar antes de la siguiente captura
        time.sleep(capture_interval_seconds)
