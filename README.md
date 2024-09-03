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
```

# NightEye Server

## Configuración del Servidor con mDNS

Este documento explica cómo configurar un servidor en Windows para usar mDNS (Multicast DNS) y permitir que la Raspberry Pi envíe archivos usando un nombre de host local.


### Requisitos Previos

1. **Bonjour para Windows**: Necesitas tener Bonjour instalado en tu PC con Windows para habilitar el soporte de mDNS.
   - Descárgalo e instálalo desde [Apple's Bonjour for Windows](https://support.apple.com/kb/DL999?locale=en_US).

## Configuración en Windows

### Paso 1: Verificar Bonjour

1. **Verificar si Bonjour está instalado**:
   - Abre la terminal (cmd) y ejecuta el siguiente comando para verificar si el servicio Bonjour está en ejecución:
     ```shell
     sc query Bonjour Service
     ```
   - Si el servicio no está instalado, sigue las instrucciones para instalarlo.

2. **Asegurarse de que el servicio Bonjour está en ejecución:**
   - Ejecuta:
     ```shell
     net start "Bonjour Service"
     ```
   - Si el servicio ya está en ejecución, recibirás un mensaje que indica que el servicio ya está iniciado.
3. **Obtencion del server Hostname (PC):**
   - Ejecucion:
    ```bash
    hostname
    ```
    El resultado obtenido por este comando lo usaremos para acceder al servidor sin conocer la ip exacta. Bonjour asignará automáticamente un nombre de host en la forma hostname.local, donde hostname es el nombre de tu PC.

### Paso 2: Configura la Raspberry Pi para Usar mDNS

Instala y Configura Avahi en la Raspberry Pi:

- **Instala Avahi:**

    Avahi es el sistema mDNS en Linux. Instálalo ejecutando el siguiente comando en tu Raspberry Pi:

    ```bash
    sudo apt update
    sudo apt install avahi-daemon avahi-utils
    ```

- **Configura la Raspberry Pi:**
    Después de instalar Avahi, debería comenzar a resolver nombres de host en la red local automáticamente.