"""
This module has functions to read the usage of resources and perform ping operations.
"""

import re
import os
import csv
import subprocess
import threading
from typing import List, Optional, Tuple

import psutil


def ping(ip: str) -> Optional[float]:
    """
    Sends a single ping request to the specified IP address and returns the
    response time in seconds.

    Args:
        ip (str): The IP address or hostname to ping.

    Returns:
        Optional[float]: The round-trip time in seconds.
        Returns None if the ping fails or if the response time cannot be obtained.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "1", ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        time = re.search(r"time=(\d+\.?\d*) ms", result.stdout)
        if time:
            response_time = float(time.group(1))  # Convert milliseconds to seconds
            return response_time
        else:
            print(f"No se pudo obtener el tiempo de respuesta del ping a {ip}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error haciendo ping a {ip}: {e.stderr}")
        return None


def get_system_usage(interval: float = 1) -> Tuple[float, float]:
    """
    Gets the current CPU and memory usage of the system.

    Returns:
        Tuple[float, float]: A tuple containing the CPU usage and memory usage,
        both expressed as values between 0 and 1. The first element is the CPU usage,
        and the second element is the memory usage.
    """
    cpu_usage = psutil.cpu_percent(interval=interval) / 100.0
    memory = psutil.virtual_memory()
    memory_usage = memory.percent / 100.0

    return cpu_usage, memory_usage


def measure_resources_during_prediction(
    prediction_function, *args, **kwargs
) -> Tuple[float, float]:
    """
    Measures CPU and memory usage while performing a prediction.

    Args:
        prediction_function (callable): The function to perform the prediction.
        *args: Positional arguments for the prediction function.
        **kwargs: Keyword arguments for the prediction function.

    Returns:
        Tuple[float, float]: Average CPU and memory usage during the prediction.
    """
    cpu_usages: List[float] = []
    memory_usages: List[float] = []
    stop_event = threading.Event()

    # Function to measure system usage in a separate thread
    def measure():
        while not stop_event.is_set():
            cpu_usage, memory_usage = get_system_usage(interval=0.1)
            cpu_usages.append(cpu_usage)
            memory_usages.append(memory_usage)

    # Start measuring in a separate thread
    resource_thread = threading.Thread(target=measure)
    resource_thread.start()

    # Perform the prediction
    results_data = prediction_function(*args, **kwargs)

    # Stop measuring and wait for the thread to finish
    stop_event.set()
    resource_thread.join()

    # Calculate the average CPU and memory usage
    avg_cpu_usage = sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0
    avg_memory_usage = sum(memory_usages) / len(memory_usages) if memory_usages else 0

    return avg_cpu_usage, avg_memory_usage, results_data


def store_results(
    csv_path: str,
    image_size: int,
    processing_time: float,
    cpu_usage: float,
    memory_usage: float,
    results_data: dict,
    detection_place: str,
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
            "detection_place",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not os.path.isfile(csv_path):
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
                "detection_place": detection_place,
            }
        )
