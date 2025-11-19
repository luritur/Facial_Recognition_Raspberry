from gpiozero import Button, LED
import threading
import queue
import time
import cv2
def run(frames, duracion, show=True, camera_index=0):
    cap = cv2.VideoCapture(camera_index)  # Abre la cámara (ojo con el 0)
    if not cap.isOpened():
        print("run.py: no se pudo abrir la cámara.")
        return
    print(f"run.py: captura iniciada durante {duracion} segundos")
    inicio = time.time()
    frames_put=0

    while time.time() - inicio < duracion: #x segundos de while (se pasa como parametro)
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer el frame.")
            break
        frames.put(frame)
        frames_put+=1

        # Mostrar frame opcional (chateada)
        if show:
            cv2.imshow("Cámara", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
                break

    cap.release()
    if show:
        cv2.destroyAllWindows()
    print(f"run.py: captura finalizada. Frames encolados: {frames_put}")
