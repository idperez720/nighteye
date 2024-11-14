"""This module contains the functions to perform local detection using YOLOv8."""

import os
import requests


def upload_image(image_path: str, server_ip: str = None) -> str:
    """
    Envía la imagen al servidor y descarga el resultado en la carpeta './data/server/'.

    Args:
        image_path (str): Ruta de la imagen a enviar.
    Returns:
        str: Ruta del archivo procesado descargado.
    """
    # Crear la carpeta de resultados si no existe
    result_folder = "./data/server/"
    os.makedirs(result_folder, exist_ok=True)
    if server_ip is None:
        server_ip = "192.168.2.10"

    url = f"http://{server_ip}:8000/"
    with open(image_path, "rb") as f:
        headers = {
            "X-File-Name": os.path.basename(image_path),
            "Content-type": "image/jpeg",
        }
        response = requests.post(url, headers=headers, data=f, timeout=120)

        # Guardar la imagen procesada en './data/server/'
        result_image_path = os.path.join(
            result_folder,
            f"{os.path.basename(image_path).split('.')[0]}_server_result.jpg",
        )
        with open(result_image_path, "wb") as result_file:
            result_file.write(response.content)

    print(f"Processed image downloaded at: {result_image_path}")
    return result_image_path
