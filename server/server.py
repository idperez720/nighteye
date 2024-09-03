""" Servidor HTTP para recibir archivos"""

import http.server
import socketserver
import os
from detection import init_model, image_prediction

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

        # Asumiendo que los archivos son enviados directamente como binarios
        file_name = self.headers.get("X-File-Name", "uploaded_file.png")
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        with open(file_path, "wb") as f:
            f.write(post_data)
        if "result" not in file_name:
            model = init_model()
            image_prediction(model, file_path)

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"File uploaded successfully")


with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
