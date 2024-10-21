""" Main file to run the server. """

import argparse
from detection_v2.image_capture import capture_and_process_images


def main():
    """Main function of the script."""
    parser = argparse.ArgumentParser(description="Captura y procesa imágenes.")
    parser.add_argument(
        "--server_ip",
        type=str,
        default=None,
        help="IP del servidor para realizar inferencia si es necesario",
    )
    parser.add_argument(
        "--total_duration",
        type=int,
        default=10,
        help="Duración total de la captura en segundos",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=2,
        help="Intervalo entre capturas en segundos",
    )
    args = parser.parse_args()

    # Captura y procesa imágenes
    capture_and_process_images(
        output_folder="data_local_results",  # Puedes cambiar esto a una carpeta de salida deseada
        total_duration=args.total_duration,
        interval=args.interval,
        server_ip=args.server_ip
    )


if __name__ == "__main__":
    main()