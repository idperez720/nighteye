import cv2
import os
import time
from ultralytics import YOLO
from datetime import datetime

def image_prediction(image_path: str):
    model = YOLO("models/yolov8n.pt")
    # model.export(format="ncnn")
    # ncnn_model = YOLO("models/yolov8n_ncnn_model")
    results = model(image_path)
    results[0].save(f"{image_path.split('.')[0]}_result.jpg")


# Crear una nueva carpeta para cada ejecución
execution_folder = datetime.now().strftime("%Y%m%d_%H%M%S")
output_folder = os.path.join("data_collection", execution_folder)
os.makedirs(output_folder, exist_ok=True)

# Abre la cámara (normalmente, 0 es la cámara predeterminada)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se puede abrir la cámara")
    exit()

# Duración total en segundos y intervalo de captura en segundos
total_duration = 10
interval = 2
start_time_total = time.time()
start_time = time.time()
condition = False

while not condition:
    # Captura frame por frame
    ret, frame = cap.read()

    # Si no se pudo leer el frame, salir
    if not ret:
        print("Error: No se puede recibir frame (finalizando...)")
        break

    # Calcula el tiempo transcurrido desde el inicio
    current_time = time.time()
    elapsed_time = current_time - start_time_total
    curent_elapsed_time = current_time - start_time
    elapsed_time_sec = int(elapsed_time)
    if elapsed_time_sec == 12:
        condition = True

    # Agrega el tiempo transcurrido al frame
    cv2.putText(frame, f"Tiempo transcurrido: {elapsed_time_sec}s",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Verifica si han pasado 3 segundos
    if curent_elapsed_time >= interval:
        print(elapsed_time)
        # Guardar la imagen en la carpeta de salida
        image_name = f"photo_{elapsed_time_sec}.png"
        image_path = os.path.join(output_folder, image_name)
        cv2.imwrite(image_path, frame)
        print(f"Foto guardada en: {image_path}")
        image_prediction(image_path)
        os.remove(image_path)
        # Reinicia el temporizador
        start_time = time.time()

    # Verifica si se ha alcanzado la duración total
    if elapsed_time >= total_duration:
        print("Finalizando captura de fotos...")
        break

    # Si presionas la tecla 'q', sale del bucle
    # En un entorno sin interfaz gráfica, este código no funcionará

# Libera la cámara
cap.release()
