""" This module contains functions for running detection tests, capturing images at intervals"""

import os
import time
from utils.detection import upload_image, image_prediction, init_model
from utils.computer_resources import measure_resources_during_prediction, store_results

from utils.image_capture import initialize_camera, capture_and_save_image


'''def run_detection_tests(
    capture_interval_seconds: int = 0.5,
    output_folder: str = "./data/local/",
    output_csv: str = "./data/tests/",
    server_ip: str = None,
    # duration_minutes: int = 5,
    n: int = 2,
    rate_threshold: float = 0.1,
) -> None:
    """Runs detection tests, capturing images at intervals for a set duration and logging
    resource usage.

    Args:
        duration_minutes (int): Duration to run the test in minutes.
        capture_interval_seconds (int): Interval between captures in seconds.
        output_folder (str): Folder where the images will be saved.
        output_csv (str): Path to the output CSV file.
        server_ip (str): IP address of the server for uploading images.
        n (int): Number of images to process with `server_detection` after resource threshold breach
    """
    # Ensure output directories exist
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_csv, exist_ok=True)
    os.makedirs("./data/local/smoke_capture", exist_ok=True)

    # Initialize camera
    try:
        cap = initialize_camera()
    except RuntimeError as e:
        print(f"Camera initialization failed: {e}")
        return

    model = init_model(size="n", rpi=True)

    start_time = time.time()
    # end_time = start_time + duration_minutes * 60
    photo_count = 0
    use_server_detection = False
    images_with_server_detection = 0
    local_processing_count = 0
    last_cpu_usage = None
    last_memory_usage = None
    detection_place = None

    photo_paths = [
        f
        for f in os.listdir(output_folder)
        if os.path.isfile(os.path.join(output_folder, f))  # Check if it's a file
        and f.lower().endswith((".jpg", ".jpeg", ".png"))  # Check if it's an image
        and "result" not in f.lower()  # Exclude files with 'result' in their name
    ]

    for photo in photo_paths:
        # Capture and save image
        # photo_name = f"photo_{int(time.time() * 1000)}.jpg"
        image_path = os.path.join("./data/local/smoke_capture/", photo)
        try:
            capture_and_save_image(cap, image_path)
        except (IOError, RuntimeError) as e:
            print(f"Failed to capture image: {e}")
            continue

        image_path = os.path.join(output_folder, photo)
        photo_count += 1
        # Measure resource usage during prediction
        try:
            start_processing_time = time.time()
            # Choose the function dynamically based on resource usage
            if use_server_detection and images_with_server_detection < n:
                if local_processing_count >= 2:
                    detection_place = "server"
                    avg_cpu_usage, avg_memory_usage, results_data = (
                        measure_resources_during_prediction(
                            lambda image_path=image_path: upload_image(
                                image_path=image_path, server_ip=server_ip
                            )
                        )
                    )
                    processing_time = time.time() - start_processing_time
                    images_with_server_detection += 1
                else:
                    avg_cpu_usage, avg_memory_usage, results_data = (
                        measure_resources_during_prediction(
                            lambda image_path=image_path: upload_image(
                                image_path=image_path, server_ip=server_ip
                            )
                        )
                    )
                    processing_time = time.time() - start_processing_time
                    use_server_detection = (
                        False  # Force local processing if less than 2 local
                    )
            else:
                detection_place = "local"
                avg_cpu_usage, avg_memory_usage, results_data = (
                    measure_resources_during_prediction(
                        lambda image_path=image_path: image_prediction(
                            model=model, image_path=image_path
                        )
                    )
                )
                processing_time = time.time() - start_processing_time
                use_server_detection = False  # Reset after `n` images
                local_processing_count += 1

            # Check positive resource change rate
            if last_cpu_usage is not None and last_memory_usage is not None:
                cpu_change = avg_cpu_usage - last_cpu_usage
                memory_change = avg_memory_usage - last_memory_usage
                print(
                    f"CPU change: {cpu_change*100:.2f}%, Memory change: {memory_change*100:.2f}%"
                )

                # Ensure valid positive changes
                if (
                    cpu_change > rate_threshold and avg_cpu_usage >= 0.50
                ) or memory_change > rate_threshold:
                    print(
                        f"Positive resource change detected! CPU: {cpu_change*100:.2f}%, "
                        f"Memory: {memory_change*100:.2f}%. Switching to server detection.",
                    )
                    use_server_detection = True
                    images_with_server_detection = 0

            # Update last resource usage
            last_cpu_usage = avg_cpu_usage
            last_memory_usage = avg_memory_usage

            # Store results in CSV
            store_results(
                os.path.join(
                    output_csv, f"resource_usage_{int(start_time * 1000)}.csv"
                ),
                image_size=os.path.getsize(image_path),
                processing_time=processing_time,
                cpu_usage=avg_cpu_usage,
                memory_usage=avg_memory_usage,
                results_data=results_data,
                detection_place=detection_place,
            )
        except (IOError, RuntimeError) as e:
            print(f"Error during prediction or logging: {e}")
            continue

        # Log resource usage
        print(
            f"Capture {photo_count} at {time.strftime('%H:%M:%S')}, "
            f"CPU: {avg_cpu_usage*100:.2f}%, Memory: {avg_memory_usage*100:.2f}%"
        )
        print("=" * 50)

        # Wait for the next capture
        time.sleep(capture_interval_seconds)

    print(f"Detection test completed. Total photos taken: {photo_count}")
    print(f"Data saved to {output_csv}")'''





def run_detection_tests(
    capture_interval_seconds: float = 2,
    output_folder: str = "./data/local/",
    output_csv: str = "./data/tests/",
    server_ip: str = None,
    image_ext: str = "jpg",
    n: int = 2,
    rate_threshold: float = 0.012,
) -> None:
    """Runs detection tests with optional server-based inference based on system resource usage."""

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_csv, exist_ok=True)

    try:
        cap = initialize_camera()
    except RuntimeError as e:
        print(f"Camera initialization failed: {e}")
        return

    model = init_model(size="n", rpi=True)

    start_time = time.time()
    photo_count = 0
    use_server_detection = False
    images_with_server_detection = 0
    local_processing_count = 0
    last_cpu_usage = None
    last_memory_usage = None

    contador_aumentos = 0
    ultimo_valor = None
    

    # CSV único para toda la sesión
    csv_path = os.path.join(output_csv, f"resource_usage_delegation_{int(start_time * 1000)}.csv")

    while True:
        try:
            # Captura y guarda imagen
            image_path = capture_and_save_image(cap, output_folder, image_ext)
            photo_count += 1

            # Detección (local o en servidor)
            start_processing_time = time.time()

            if use_server_detection and images_with_server_detection < n:
                detection_place = "server"
                avg_cpu_usage, avg_memory_usage, results_data, current_memory = measure_resources_during_prediction(
                    lambda image_path=image_path: upload_image(image_path=image_path, server_ip=server_ip, image_extension=image_ext)
                )
                images_with_server_detection += 1
            else:
                detection_place = "local"
                avg_cpu_usage, avg_memory_usage, results_data, current_memory = measure_resources_during_prediction(
                    lambda image_path=image_path: image_prediction(model=model, image_path=image_path, image_extension=image_ext)
                )
                use_server_detection = False
                local_processing_count += 1
                images_with_server_detection = 0

            processing_time = time.time() - start_processing_time



            '''# Evaluación de uso de recursos
            if last_cpu_usage is not None and last_memory_usage is not None:
                cpu_change = avg_cpu_usage - last_cpu_usage
                memory_change = avg_memory_usage - last_memory_usage


                """if (cpu_change > rate_threshold and avg_cpu_usage >= 0.5) or memory_change > rate_threshold:
                    print(
                        f"Positive resource change detected! CPU: {cpu_change*100:.2f}%, "
                        f"Memory: {memory_change*100:.2f}%. Switching to server detection."
                    )
                    use_server_detection = True
                    images_with_server_detection = 0"""
                
                if memory_change > rate_threshold:
                    print(
                        f"Memory: {memory_change*100:.2f}%. Switching to server detection."
                    )
                    use_server_detection = True
                    images_with_server_detection = 0

            last_cpu_usage = avg_cpu_usage
            last_memory_usage = avg_memory_usage'''







            # Evaluación de uso de recursos
            if last_cpu_usage is not None and last_memory_usage is not None and ultimo_valor is not None:
                cpu_change = avg_cpu_usage - last_cpu_usage
                memory_change = avg_memory_usage - last_memory_usage
               
                if current_memory > ultimo_valor:
                    contador_aumentos += 1
                else:
                    contador_aumentos = 0

                
                if memory_change > rate_threshold or contador_aumentos == 4:
                    print(
                        f"Memory: {memory_change*100:.2f}%. Switching to server detection."
                    )
                    use_server_detection = True
                    images_with_server_detection = 0
                    contador_aumentos = 0

            last_cpu_usage = avg_cpu_usage
            last_memory_usage = avg_memory_usage
            ultimo_valor = current_memory



















            # Guardado de resultados
            '''store_results(
                os.path.join(output_csv, f"resource_usage_{int(start_time * 1000)}.csv"),
                image_size=os.path.getsize(image_path),
                processing_time=processing_time,
                cpu_usage=avg_cpu_usage,
                memory_usage=avg_memory_usage,
                results_data=results_data,
                detection_place=detection_place,
            )'''
            store_results(
                csv_path,
                image_size=os.path.getsize(image_path),
                processing_time=processing_time,
                cpu_usage=avg_cpu_usage,
                memory_usage=avg_memory_usage,
                results_data=results_data,
                detection_place=detection_place,
            )

            print(
                f"Capture {photo_count} at {time.strftime('%H:%M:%S')}, "
                f"CPU: {avg_cpu_usage*100:.2f}%, Memory: {avg_memory_usage*100:.2f}%"
            )
            print("=" * 50)

            time.sleep(capture_interval_seconds)

        except (IOError, RuntimeError) as e:
            print(f"[ERROR] Error durante procesamiento: {e}")
            continue
