# Usa la imagen base de Ultralytics
FROM ultralytics/ultralytics:latest-arm64

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Copia todo el contenido de tu repositorio al contenedor
COPY . .

# Ejecuta el script principal
CMD ["python", "app/local/local_detection.py"]
