import cv2

# Abre la cámara (normalmente, 0 es la cámara predeterminada)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Error: No se puede abrir la cámara")
    exit()

while True:
    # Captura frame por frame
    ret, frame = cap.read()

    # Si no se pudo leer el frame, salir
    if not ret:
        print("Error: No se puede recibir frame (finalizando...)")
        break

    # Muestra el frame en una ventana llamada 'frame'
    cv2.imshow("frame", frame)

    # Si presionas la tecla 'q', sale del bucle
    if cv2.waitKey(1) == ord("q"):
        break

# Libera la cámara y cierra todas las ventanas
cap.release()
cv2.destroyAllWindows()
