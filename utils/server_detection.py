""" Módulo que contiene funciones para la detección de objetos en imágenes. """
from ultralytics import YOLO


def init_model() -> YOLO:
    """Inicializa el modelo YOLO y lo exporta a NCNN.

    Returns:
        YOLO: Modelo YOLO exportado a NCNN.
    """
    model = YOLO("models/yolov8x.pt")
    return model

def image_prediction(model: YOLO, image_path: str) -> str:
    """
    Realiza la predicción en la imagen y guarda el resultado.

    Args:
        image_path (str): Ruta de la imagen de entrada.

    Returns:
        str: Ruta del archivo de resultado.
    """
    results = model(image_path)
    result_path = f"{image_path.split('.')[0]}_result.jpg"
    results[0].save(result_path)
    return result_path
