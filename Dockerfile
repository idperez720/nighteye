# Usa la imagen base de Ultralytics
FROM ultralytics/ultralytics:latest-arm64

# Instalar libgl1 para soporte de OpenGL
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Copia todo el contenido de tu repositorio al contenedor
COPY . .

# Ejecuta el script principal
CMD ["python", "local/local_detection.py"]
