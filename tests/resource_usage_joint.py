"""This module contains functions to run detection tests, capturing images at intervals
for a set duration and logging resource usage.
"""

import csv
import os
import time
from utils.detection import upload_image_preprocessed
from utils.computer_resources import measure_resources_during_prediction
from utils.image_capture import initialize_camera, capture_and_save_image


def store_results(
    csv_path: str,
    image_size: int,
    processing_time: float,
    cpu_usage: float,
    memory_usage: float,
    results_data: dict,
) -> None:
    """Stores the collected information in a CSV file.

    Args:
        csv_path (str): Path to the output CSV file.
        image_size (int): Size of the image in bytes.
        processing_time (float): Time taken to process the image.
        cpu_usage (float): Average CPU usage during processing.
        memory_usage (float): Average memory usage during processing.
        results_data (dict): Additional results data from the image prediction.
    """
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, mode="a", newline="", encoding="utf-8") as csv_file:
        fieldnames = [
            "image_size",
            "processing_time",
            "cpu_usage",
            "memory_usage",
            "image_path",
            "preprocess_time",
            "inference_time",
            "postprocess_time",
            "original_shape",
            "objects_detected",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Write the header if the file is new

        writer.writerow(
            {
                "image_size": image_size,
                "processing_time": processing_time,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "image_path": results_data.get("path", ""),
                "preprocess_time": results_data.get("speed", {}).get("preprocess", 0.0),
                "inference_time": results_data.get("speed", {}).get("inference", 0.0),
                "postprocess_time": results_data.get("speed", {}).get(
                    "postprocess", 0.0
                ),
                "original_shape": results_data.get("original_shape", ()),
                "objects_detected": results_data.get("objects_detected", []),
            }
        )


def run_detection_tests(
    duration_minutes: int = 10,
    capture_interval_seconds: int = 3,
    output_folder: str = "./data/local/",
    output_csv: str = "./data/tests/resource_usage_joint.csv",
    server_ip: int = "192.168.2.10",
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
    try:
        cap = initialize_camera()
    except RuntimeError as e:
        print(e)
        return

    start_time = time.time()
    end_time = start_time + duration_minutes * 60
    photo_count = 0

    while time.time() < end_time:
        try:
            image_path = capture_and_save_image(cap, output_folder)
            image_size = os.path.getsize(image_path)
            photo_count += 1
        except RuntimeError as e:
            print(e)
            continue

        # Measure resource usage during image prediction
        start_processing_time = time.time()
        avg_cpu_usage, avg_memory_usage, results_data = (
            measure_resources_during_prediction(
                lambda image_path=image_path: upload_image_preprocessed(
                    image_path=image_path, server_ip=server_ip
                )
            )
        )
        print(results_data)
        processing_time = time.time() - start_processing_time

        # Store the results in the CSV file
        store_results(
            output_csv,
            image_size=image_size,
            processing_time=processing_time,
            cpu_usage=avg_cpu_usage,
            memory_usage=avg_memory_usage,
            results_data=results_data,
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
