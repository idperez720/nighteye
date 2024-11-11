import os
import time
import cv2
import psutil
import csv
from utils.local_detection import image_prediction, init_model


def run_detection_tests(
    num_captures: int = 100,
    output_folder: str = "./data_local_results/",
    output_csv: str = "./data_local_results/tests/detection_results.csv",
) -> None:
    """This function captures images from the camera, processes them, and saves
    the data to a CSV file.

    Args:
        output_folder (str): Folder where the images will be saved.
        num_captures (int): Number of images to capture.
        output_csv (str): Path to the output CSV file.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se puede abrir la cámara")
        return

    # Inicializa el modelo una vez
    model = init_model()

    # Abre el archivo CSV para escribir los datos
    with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Escribe los encabezados
        writer.writerow(["Captura", "CPU_Durante", "Memory_Durante"])

        for i in range(num_captures):
            ret, frame = cap.read()
            if not ret:
                print("Error: No se puede recibir frame (finalizando...)")
                break

            # Guarda la imagen en el disco (opcional, solo para referencia)
            timestamp = int(time.time() * 1000)
            image_name = f"photo_{timestamp}.png"
            image_path = os.path.join(output_folder, image_name)
            cv2.imwrite(image_path, frame)

            # Mide el uso de recursos durante el procesamiento
            cpu_usages = []
            memory_usages = []

            # Inicia la medición del tiempo
            start_time = time.time()

            # Realiza la inferencia y mide el uso de recursos continuamente
            while time.time() - start_time < 0.1:  # Intervalo de medición de 100 ms
                cpu_usages.append(psutil.cpu_percent(interval=0.1))
                memory_usages.append(psutil.virtual_memory().percent)

            # Realiza la inferencia (puedes ajustar el tiempo de medición según sea necesario)
            _ = image_prediction(model=model, image_path=image_path)

            # Calcula el promedio de uso de CPU y memoria durante la inferencia
            avg_cpu_usage = sum(cpu_usages) / len(cpu_usages)
            avg_memory_usage = sum(memory_usages) / len(memory_usages)

            # Escribe los datos en el archivo CSV
            writer.writerow([i + 1, avg_cpu_usage, avg_memory_usage])

            # Imprime el log de cada línea escrita
            print(
                f"Escribiendo en CSV: Captura {i + 1}, CPU: {avg_cpu_usage:.2f}%, Memoria: {avg_memory_usage:.2f}%"
            )

            # División visual para indicar cambio de imagen
            print("=" * 50 + f" Fin de captura {i + 1} " + "=" * 50)

    cap.release()
    print(f"Finalizando prueba de detección... Datos guardados en {output_csv}")
