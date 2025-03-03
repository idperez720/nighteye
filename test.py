"""Run test cases for the resource usage detection module."""

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
    args = parser.parse_args()

    if args.type_inference == "local":
        print("Tests local")
        run_detection_tests()
    elif args.type_inference == "server":
        print("Tests en el servidor")
        run_detection_tests_server(server_ip=args.server_ip)
    elif args.type_inference == "delegation":
        print("Tests Task Delegation en conjunta")
        run_detection_tests_delegation(server_ip=args.server_ip)
    else:
        print("Tipo de inferencia no válido: local, server, joint")
