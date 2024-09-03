# NightEye Lite (Raspberry execution)

## Requisitos
- Raspberry Pi con Ubuntu 24.04.1 LTS aarch64
- Conexión a Internet

## Instalación y ejecución

Clona el repositorio y ejecuta el script de instalación:

```bash
git clone https://github.com/idperez720/nighteye.git
cd nighteye

### Si no tienes conda ejecutar el comando
bash install_conda.sh

Este script instalará Miniconda si es necesario

### Crear el ambiente
conda env create -f environment.yml

### Ejecucion deteccion en local
python local/local_detection.py