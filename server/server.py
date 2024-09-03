import http.server
import socketserver
import os
from urllib.parse import parse_qs

PORT = 8000
UPLOAD_FOLDER = (
    "C:/Users/ivand/nighteye_server"  # Reemplaza con el directorio de destino
)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)

        # Asumiendo que los archivos son enviados directamente como binarios
        file_name = self.headers.get("X-File-Name", "uploaded_file.png")
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        with open(file_path, "wb") as f:
            f.write(post_data)

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"File uploaded successfully")


with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
