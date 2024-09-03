# NightEye Lite (Raspberry execution)

## Requisitos
- Raspberry Pi con Raspberry Pi OS (Debian-based)
- Conexión a Internet

## Instalación y ejecución

Clona el repositorio y ejecuta el script de instalación:

```bash
git clone <tu-repositorio-url>
cd <nombre-del-repositorio>
bash install.sh


Este script instalará Miniconda si es necesario, configurará el entorno Conda y ejecutará el programa.

### 4. Probar y desplegar
Una vez que hayas creado los archivos `environment.yml` y `install.sh`, asegúrate de probar el script en una Raspberry Pi para verificar que todo funcione como se espera. 

### 5. Version Control
Asegúrate de agregar los archivos `install.sh` y `environment.yml` a tu control de versiones para que otros usuarios puedan utilizarlos.

Con este enfoque, podrás clonar el repositorio y ejecutar un único comando (`bash install.sh`) para configurar todo el entorno y ejecutar tu programa en la Raspberry Pi.
