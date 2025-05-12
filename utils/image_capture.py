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


def save_image(frame, output_folder: str, image_extension: str) -> str:
    """Saves the captured frame to the specified folder.

    Args:
        frame: The image frame to save.
        output_folder (str): Folder where the image will be saved.

    Returns:
        str: Path to the saved image.
    """
    timestamp = int(time.time() * 1000)
    image_name = f"photo_{timestamp}.{image_extension}"
    image_path = os.path.join(output_folder, image_name)
    cv2.imwrite(image_path, frame)
    return image_path

''' función test PT
def save_image(frame, output_folder: str, image_extension: str) -> str:
    """Saves the captured frame to the specified folder.

    Args:
        frame: The image frame to save.
        output_folder (str): Folder where the image will be saved.

    Returns:
        str: Path to the saved image.
    """
    if frame is None or frame.size == 0:
        raise ValueError("[CLIENT ERROR] Frame vacío o no válido")

    timestamp = int(time.time() * 1000)
    image_name = f"photo_{timestamp}.{image_extension}"
    image_path = os.path.join(output_folder, image_name)

    success = cv2.imwrite(image_path, frame)
    if not success or not os.path.exists(image_path) or os.path.getsize(image_path) == 0:
        raise ValueError("[CLIENT ERROR] No se pudo guardar la imagen correctamente")

    return image_path'''





def capture_and_save_image(cap: cv2.VideoCapture, output_folder: str, image_extension: str) -> str:
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
    return save_image(frame, output_folder, image_extension)


    '''función test PT
    if not ret or frame is None or frame.size == 0:
        raise ValueError("[CLIENT ERROR] Fallo al capturar la imagen desde la cámara")

    return save_image(frame, output_folder, image_extension)
    
    #os.path.dirname(image_path)