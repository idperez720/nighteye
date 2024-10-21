""" Server detection script """

from datetime import datetime
import os
from detection_v2.image_capture import capture_and_process_images

def main(duracion_total: int = 12, intervalo: int = 3, server_ip: str = None) -> None:
    """Función principal del script"""
    # Captura y procesa imágenes
    execution_folder = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join("data_local_results", execution_folder)
    os.makedirs(output_folder, exist_ok=True)
    capture_and_process_images(output_folder, duracion_total, intervalo, server_ip)

if __name__ == "__main__":
    main()