""" This is the main file for the server. """
from server.server import main as server_main




if __name__ == "__main__":
    server_main()

"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Captura y procesa imágenes.")
    parser.add_argument(
        "--image_format",
        type=str,
        default=None,
        help="Formato de Imagen",
    )
    args = parser.parse_args()

    elif args.type_inference == "server":
        print("Tests en el servidor")
        server_main(image_ext=args.image_format)
"""
