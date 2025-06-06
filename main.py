""" Main file to run the server. """

import argparse
from joint.joint_detection import main as joint_detection
from local.detection import main as local_main
from server.detection import main as server_main


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


def main():
    """Función principal del script."""
    # Crear una nueva carpeta para cada ejecución
    # Configuración de argparse para recibir parámetros
    # ipMac = 192.168.2.25
    # ipPC = 192.168.2.14

    parser = argparse.ArgumentParser(description="Captura y procesa imágenes.")
    parser.add_argument(
        "--total_duration",
        type=int,
        default=10,
        help="Duración total de la captura en segundos",
    )
    parser.add_argument(
        "--interval", type=int, default=2, help="Intervalo entre capturas en segundos"
    )
    parser.add_argument(
        "--type_inference",
        type=str,
        default="local",
        help="Realizar inferencia en el servidor",
    )
    parser.add_argument(
        "--server_ip",
        type=str,
        default=None,
        help="Realizar inferencia en el servidor",
    )
    parser.add_argument(
        "--rpi",
        type=str2bool,
        default=True,
        help="Execution on Raspberry Pi (default: True).",
    )
    parser.add_argument(
        "--image_format",
        type=str,
        default=None,
        help="Formato de Imagen",
    )
    args = parser.parse_args()

    # Crear una nueva carpeta para cada ejecución
    if args.type_inference == "local":
        print("Inferencia local")
        local_main(args.total_duration, args.interval, args.rpi, args.image_format)
    elif args.type_inference == "server":
        print("Inferencia en el servidor")
        server_main(args.total_duration, args.interval, args.server_ip, args.image_format)
    elif args.type_inference == "joint":
        print("Inferencia en conjunta")
        joint_detection(args.total_duration, args.interval, args.server_ip, args.image_format)
    else:
        print("Tipo de inferencia no válido: local, server, joint")
        return None


if __name__ == "__main__":
    main()
