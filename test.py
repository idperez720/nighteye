"""Run test cases for the resource usage detection module."""

from main import str2bool
import argparse
from tests.resource_usage import run_detection_tests
from tests.resource_usage_server import (
    run_detection_tests as run_detection_tests_server,
)
from tests.resource_usage_delegation import (
    run_detection_tests as run_detection_tests_delegation,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Captura y procesa imágenes.")
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
        "--image_format",
        type=str,
        default="png",
        help="Formato de Imagen",
    )
    parser.add_argument(
        "--rpi",
        type=str2bool,
        default=True,
        help="Execution on Raspberry Pi (default: True).",
    )
    parser.add_argument(
        "--duration_minutes",
        type=int,
        default=10,
        help="Duración de la ejecución en minutos.",
    )
    parser.add_argument(
        "--interval_seconds",
        type=int,
        default=2,
        help="Intervalo entre capturas en segundos.",
    )

    args = parser.parse_args()

    if args.type_inference == "local":
        print("Tests local")
        run_detection_tests(
            image_ext=args.image_format,
            rpi=args.rpi,
            duration_minutes=args.duration_minutes,
            capture_interval_seconds=args.interval_seconds,
        )
    elif args.type_inference == "server":
        print("Tests en el servidor")
        run_detection_tests_server(
            server_ip=args.server_ip, image_ext=args.image_format
        )
    elif args.type_inference == "delegation":
        print("Tests Task Delegation en conjunta")
        run_detection_tests_delegation(
            server_ip=args.server_ip, image_ext=args.image_format
        )
    else:
        print("Tipo de inferencia no válido: local, server, joint")
