import csv
import os
import time
import cv2
from utils.local_detection import image_prediction, init_model
from utils.computer_resources import measure_resources_during_prediction


def initialize_camera() -> cv2.VideoCapture:
    """Initializes the camera for capturing images.

    Returns:
        cv2.VideoCapture: The initialized camera object.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Error: Unable to open the camera.")
    return cap


def save_image(frame, output_folder: str) -> str:
    """Saves the captured frame to the specified folder.

    Args:
        frame: The image frame to save.
        output_folder (str): Folder where the image will be saved.

    Returns:
        str: Path to the saved image.
    """
    timestamp = int(time.time() * 1000)
    image_name = f"photo_{timestamp}.png"
    image_path = os.path.join(output_folder, image_name)
    cv2.imwrite(image_path, frame)
    return image_path


def capture_and_save_image(cap: cv2.VideoCapture, output_folder: str) -> str:
    """Captures an image from the camera and saves it to the output folder.

    Args:
        cap (cv2.VideoCapture): Video capture object.
        output_folder (str): Folder where the image will be saved.

    Returns:
        str: Path to the saved image.
    """
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("Error: Unable to receive frame (terminating...)")
    return save_image(frame, output_folder)


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


# def run_detection_tests(
#     num_captures: int = 10,
#     output_folder: str = "./data_local_results/raw_photos",
#     output_csv: str = "./data_local_results/tests/resource_usage.csv",
# ) -> None:
#     """Runs detection tests, capturing images, processing them, and logging resource usage.

#     Args:
#         num_captures (int): Number of images to capture.
#         output_folder (str): Folder where the images will be saved.
#         output_csv (str): Path to the output CSV file.
#     """
#     # Initialize camera and model
#     try:
#         cap = initialize_camera()
#     except RuntimeError as e:
#         print(e)
#         return

#     model = init_model()

#     for i in range(num_captures):
#         try:
#             image_path = capture_and_save_image(cap, output_folder)
#             image_size = os.path.getsize(image_path)
#         except RuntimeError as e:
#             print(e)
#             continue

#         # Measure resource usage during image prediction
#         start_time = time.time()
#         avg_cpu_usage, avg_memory_usage, results_data = (
#             measure_resources_during_prediction(
#                 lambda image_path=image_path: image_prediction(
#                     model=model, image_path=image_path
#                 )
#             )
#         )
#         processing_time = time.time() - start_time
#         # Store the results in the CSV file
#         store_results(
#             output_csv,
#             image_size=image_size,
#             processing_time=processing_time,
#             cpu_usage=avg_cpu_usage,
#             memory_usage=avg_memory_usage,
#             results_data=results_data,
#         )

#         # Log resource usage
#         print(
#             f"Capture {i + 1}, CPU: {avg_cpu_usage*100:.2f}%, Memory: {avg_memory_usage*100:.2f}%"
#         )
#         print("=" * 50 + f" End of capture {i + 1} " + "=" * 50)

#     cap.release()
#     print(f"Detection test completed. Data saved to {output_csv}")


def run_detection_tests(
    num_captures: int = 10,
    output_folder: str = "./data_local_results/raw_photos",
    output_csv: str = "./data_local_results/tests/resource_usage.csv",
) -> None:
    try:
        cap = initialize_camera()
    except RuntimeError as e:
        print(e)
        return

    image_path = capture_and_save_image(cap, output_folder)

    print(image_path)
