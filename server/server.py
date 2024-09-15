"""Servidor HTTP para recibir archivos y realizar detección"""

import http.server
import socketserver
import os
from io import BytesIO
from detection import init_model, image_prediction  # pylint: disable=E0401

PORT = 8000
UPLOAD_FOLDER = "C:/Users/ivand/nighteye_server"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """Clase para manejar las peticiones HTTP"""

    def do_POST(self):  # pylint: disable=C0103
        """Maneja las peticiones POST"""
        if self.path == "/upload":
            self.handle_image_upload()
        elif self.path == "/detect":
            self.handle_features_upload()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_image_upload(self):
        """Maneja la carga de imágenes para procesar y guardar el resultado"""
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        file_name = self.headers.get("X-File-Name", "uploaded_file.png")
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        with open(file_path, "wb") as f:
            f.write(post_data)

        model = init_model()
        result_path = image_prediction(model, file_path)
        os.remove(file_path)

        with open(result_path, "rb") as result_file:
            self.send_response(200)
            self.send_header("Content-type", "image/jpeg")
            self.end_headers()
            self.wfile.write(result_file.read())

    def handle_features_upload(self):
        """Maneja la carga de características y realiza la detección"""
        content_length = int(self.headers["Content-Length"])
        features_data = self.rfile.read(content_length)

        # Guardar temporalmente las características recibidas
        features_path = os.path.join(UPLOAD_FOLDER, "features.png")
        with open(features_path, "wb") as f:
            f.write(features_data)

        model = init_model()
        # Asumiendo que las características son una imagen
        result_path = image_prediction(model, features_path)
        os.remove(features_path)

        with open(result_path, "rb") as result_file:
            self.send_response(200)
            self.send_header("Content-type", "image/jpeg")
            self.end_headers()
            self.wfile.write(result_file.read())


with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
