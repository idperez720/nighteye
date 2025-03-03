"""This module contains functions to run detection tests, capturing images at intervals
for a set duration and logging resource usage.
"""

import os
import time
from utils.detection import image_prediction, init_model
from utils.computer_resources import measure_resources_during_prediction, store_results
from utils.image_capture import initialize_camera, capture_and_save_image


def run_detection_tests(
    duration_minutes: int = 10,
    capture_interval_seconds: int = 3,
    output_folder: str = "./data/local/",
    output_csv: str = "./data/tests/",
    rpi: bool = True,
    image_ext: str = None
) -> None:
    """Runs detection tests, capturing images at intervals for a set duration and logging
    resource usage.

    Args:
        duration_minutes (int): Duration to run the test in minutes.
        capture_interval_seconds (int): Interval between captures in seconds.
        output_folder (str): Folder where the images will be saved.
        output_csv (str): Path to the output CSV file.
    """
    # Initialize camera and model
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_csv, exist_ok=True)
    try:
        cap = initialize_camera()
    except RuntimeError as e:
        print(e)
        return

    model = init_model(size="n", rpi=rpi)

    start_time = time.time()
    end_time = start_time + duration_minutes * 60
    photo_count = 0
    timestamp = int(start_time * 1000)

    while time.time() < end_time:
        try:
            image_path = capture_and_save_image(cap, output_folder, image_ext)
            image_size = os.path.getsize(image_path)
            photo_count += 1
        except RuntimeError as e:
            print(e)
            continue

        # Measure resource usage during image prediction
        start_processing_time = time.time()
        avg_cpu_usage, avg_memory_usage, results_data = (
            measure_resources_during_prediction(
                lambda image_path=image_path: image_prediction(
                    model=model, image_path=image_path
                )
            )
        )
        processing_time = time.time() - start_processing_time
        # Store the results in the CSV file
        store_results(
            f"{output_csv}resource_usage_{timestamp}.csv",
            image_size=image_size,
            processing_time=processing_time,
            cpu_usage=avg_cpu_usage,
            memory_usage=avg_memory_usage,
            results_data=results_data,
            detection_place="local",
        )

        # Log resource usage
        print(
            f"Capture {photo_count} at {time.strftime('%H:%M:%S')}, "
            f"CPU: {avg_cpu_usage*100:.2f}%, Memory: {avg_memory_usage*100:.2f}%"
        )
        print("=" * 50)

        # Wait for the next capture
        time.sleep(capture_interval_seconds)

    cap.release()
    print(f"Detection test completed. Total photos taken: {photo_count}")
    print(f"Data saved to {output_csv}")
