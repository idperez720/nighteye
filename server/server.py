"""HTTP Server to receive files and perform object detection predictions"""

import http.server
import socketserver
import os
import json
import mimetypes
from typing import Any, Dict
import numpy as np
from utils.detection import init_model, image_prediction
from utils.detection import predict_with_flatten_array, get_bounding_boxes

# Configuration for the port and upload directory
PORT = 8000
UPLOAD_FOLDER = "./data/server/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """Custom class to handle HTTP requests"""

    def do_POST(self):
        """Handles POST requests to receive and process files or image data"""
        print(self.headers) ## 

        """     ##
        transfer_encoding = self.headers.get("Transfer-Encoding")
        if transfer_encoding == "chunked":
            print("Transfer-Encoding: chunked detected, discarding request silently.")
            try:
                while True:
                    chunk_size_str = self.rfile.readline().strip()
                    if not chunk_size_str:
                        continue
                    chunk_size = int(chunk_size_str, 16)
                    if chunk_size == 0:
                        break
                    self.rfile.read(chunk_size)
                    self.rfile.read(2)  # CRLF
            except Exception as e:
                print(f"Error while discarding chunked data: {e}")
        
            # RESPONDER NORMAL para que el cliente no note error
            self.send_response(200)
            self.end_headers()
            return

        content_length_header = self.headers.get("Content-Length")
        if content_length_header is None:
            print("No Content-Length header. Discarding silently.")
            self.send_response(200)
            self.end_headers()
            return
        ##
        """


        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        content_type = self.headers.get("Content-type")
        file_name = self.headers.get("X-File-Name", "uploaded_file.png")
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        _, image_ext = os.path.splitext(file_name)

        if content_type == "application/json":
            self._handle_json_request(post_data)
        else:
            self._handle_file_request(file_path, post_data, file_name, image_ext)

    def _handle_json_request(self, post_data):
        """Handles requests with serialized image data in JSON format"""
        print("Receiving a serialized numpy array in JSON format")

        # Decode the JSON data
        json_data = json.loads(post_data)
        image_array = np.array(json_data["image_array"])
        shape = json_data["shape"]

        # Initialize the YOLO model and make predictions
        model = init_model(size="x")
        results = predict_with_flatten_array(model, image_array, shape)
        speed = results[0].speed
        original_shape = results[0].orig_shape
        boxes = results[0].boxes
        labels = results[0].names
        objects_detected = []
        for box in boxes:
            label = box.cls[0]  # Obtiene la clase del objeto
            confidence = box.conf[0].item()  # Obtiene el porcentaje de confianza
            objects_detected.append((labels[int(label)], confidence))
        results_data = {
            "speed": speed,
            "original_shape": original_shape,
            "objects_detected": objects_detected,
        }

        boxes = get_bounding_boxes(results)

        # Prepare the response with bounding box data
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
            ],
            "results_data": results_data,
        }

        self._send_json_response(response_data)

    def _handle_file_request(self, file_path, post_data, file_name, image_ext: str = None):
        """Handles requests with binary files and performs predictions if needed"""
        # Save the received file to the specified path
        with open(file_path, "wb") as file:
            file.write(post_data)
        print(f"File received: {file_name}")

        # If the file name does not contain 'result', process the image
        if "result" not in file_name:
            model = init_model()
            result_data = image_prediction(model, file_path, image_ext)

            # Send the multipart response with JSON and image
            self._send_multipart_response(result_data)
        else:
            self.send_response(400)
            self.end_headers()

    def _send_json_response(self, data):
        """Sends a JSON response back to the client"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_multipart_response(self, result_data: Dict[str, Any]):
        """
        Sends a multipart response containing JSON data and the processed image.
        """
        boundary = "----Boundary1234567890"
        self.send_response(200)
        self.send_header("Content-Type", f"multipart/mixed; boundary={boundary}")
        self.end_headers()

        # Prepare JSON part
        json_part = json.dumps(result_data).encode()
        json_headers = f"--{boundary}\r\n" "Content-Type: application/json\r\n\r\n"

        # Prepare image part
        image_path = result_data["path"]
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        image_type = mimetypes.guess_type(image_path)[0] or "application/octet-stream"
        image_headers = (
            f"--{boundary}\r\n"
            f"Content-Type: {image_type}\r\n"
            f"Content-Disposition: attachment; filename={os.path.basename(image_path)}\r\n\r\n"
        )

        # Final boundary
        final_boundary = f"--{boundary}--\r\n"

        # Write all parts to the response
        self.wfile.write(json_headers.encode())
        self.wfile.write(json_part)
        self.wfile.write(b"\r\n")
        self.wfile.write(image_headers.encode())
        self.wfile.write(image_data)
        self.wfile.write(b"\r\n")
        self.wfile.write(final_boundary.encode())

    def _send_image_response(self, image_path):
        """Sends a processed image back to the client"""
        with open(image_path, "rb") as image_file:
            self.send_response(200)
            self.send_header("Content-type", "image/jpeg")
            self.end_headers()
            self.wfile.write(image_file.read())
        print(f"Processed image sent: {image_path}")


def main():
    """Main function to start the HTTP server"""
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Server running on port {PORT}")
        httpd.serve_forever()
