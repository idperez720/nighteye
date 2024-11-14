""" This module contains functions for capturing images from the camera. """

import os
import time
import cv2


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
