""" Main file to run the server. """

import argparse
from server.joint_detection import main as joint_detection
from local.detection import main as local_main
from server.detection import main as server_main


def main():
    """Función principal del script."""
    # Crear una nueva carpeta para cada ejecución
    # Configuración de argparse para recibir parámetros
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
    args = parser.parse_args()

    # Crear una nueva carpeta para cada ejecución
    if args.type_inference == "local":
        print("Inferencia local")
        local_main(args.total_duration, args.interval)
    elif args.type_inference == "server":
        print("Inferencia en el servidor")
        server_main(args.total_duration, args.interval)
    elif args.type_inference == "joint":
        print("Inferencia en conjunta")
        joint_detection(args.total_duration, args.interval)
    else:
        print("Tipo de inferencia no válido: local, server, joint")
        return None


if __name__ == "__main__":
    main()
