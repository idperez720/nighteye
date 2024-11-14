"""Main file to run the server for image capture and processing."""

import argparse
from detection_v2.image_capture import capture_and_process_images

def str2bool(value):
    """Converts a string to a boolean value."""
    if isinstance(value, bool):
        return value
    if value.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif value.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")

def parse_arguments():
    """Parse command-line arguments."""
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

    parser.add_argument(
        "--rpi",
        type=str2bool,
        default=True,
        help="Execution on Raspberry Pi (default: True).",
    )

    return parser.parse_args()


def main():
    """Main function of the script."""
    # Parse arguments
    args = parse_arguments()

    # Capture and process images
    capture_and_process_images(
        output_folder="./data/local/",  # Customize the output folder as needed
        total_duration=args.total_duration,
        interval=args.interval,
        server_ip=args.server_ip,
    )


if __name__ == "__main__":
    main()
