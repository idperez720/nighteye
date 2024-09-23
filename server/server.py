""" Servidor HTTP para recibir archivos"""

import http.server
import socketserver
import os
import json
import numpy as np
from utils.server_detection import init_model, image_prediction
from utils.joint_detection import (
    predict_with_model,
    get_bounding_boxes,
)

PORT = 8000
UPLOAD_FOLDER = (
    "C:/Users/ivand/nighteye_server"  # Reemplaza con el directorio de destino
)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """Clase para manejar las peticiones HTTP"""

    def do_POST(self):  # pylint: disable=C0103
        """Maneja las peticiones POST"""
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        content_type = self.headers.get("Content-type")
        file_name = self.headers.get("X-File-Name", "uploaded_file.png")
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        if content_type == "application/json":
            print("Recibiendo un array de numpy serializado en JSON")

            # Decodificamos el JSON recibido
            json_data = json.loads(post_data)
            image_array = np.array(
                json_data["image_array"]
            )  # Convertimos la lista de vuelta a numpy array
            shape = json_data["shape"]
            model = init_model()
            results = predict_with_model(model, image_array, shape)
            boxes = get_bounding_boxes(results)

            response_data = {
                "bounding_boxes": [
                    {
                        "x1": box[0],
                        "y1": box[1],
                        "x2": box[2],
                        "y2": box[3],
                        "label": box[4],
                        "confidence": box[5],
                    }
                    for box in boxes
                ]
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

        else:
            # Asumiendo que los archivos son enviados directamente como binarios
            file_name = self.headers.get("X-File-Name", "uploaded_file.png")
            file_path = os.path.join(UPLOAD_FOLDER, file_name)
            with open(file_path, "wb") as f:
                f.write(post_data)
            print(file_name)
            # Si es una imagen que necesita ser procesada
            if "result" not in file_name:
                model = init_model()
                result_path = image_prediction(model, file_path)
                print("++++++++++++++++++++++++++++++++++++++")
                print(result_path)

                # Enviar la imagen procesada de vuelta al cliente
                with open(result_path, "rb") as result_file:
                    print(f"Sending processed image: {result_path}")
                    self.send_response(200)
                    self.send_header("Content-type", "image/jpeg")
                    self.end_headers()
                    self.wfile.write(result_file.read())
            else:
                self.send_response(400)
                self.end_headers()


def main():
    """Función principal para iniciar el servidor"""

    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()
