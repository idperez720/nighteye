"""HTTP Server to receive files and perform object detection predictions"""

import http.server
import socketserver
import os
import json
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
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        content_type = self.headers.get("Content-type")
        file_name = self.headers.get("X-File-Name", "uploaded_file.png")
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        if content_type == "application/json":
            self._handle_json_request(post_data)
        else:
            self._handle_file_request(file_path, post_data, file_name)

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

    def _handle_file_request(self, file_path, post_data, file_name):
        """Handles requests with binary files and performs predictions if needed"""
        # Save the received file to the specified path
        with open(file_path, "wb") as file:
            file.write(post_data)
        print(f"File received: {file_name}")

        # If the file name does not contain 'result', process the image
        if "result" not in file_name:
            model = init_model()
            result_data = image_prediction(model, file_path)
            result_path = result_data["path"]
            print(f"Processing image: {result_path}")
            self._send_image_response(result_path)
        else:
            self.send_response(400)
            self.end_headers()

    def _send_json_response(self, data):
        """Sends a JSON response back to the client"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

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
