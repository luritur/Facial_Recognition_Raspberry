import cv2
from gpiozero import Button, LED
import threading
import queue
import time
import csv
import pandas as pd
import keyboard

# Pines BCM
LED_PIN = 17
BTN_REGISTRAR = Button(23, pull_up=True)    # aumenta frecuencia
BTN_RUN = Button(24, pull_up=True)  # disminuye frecuencia
led = LED(LED_PIN)
camIndex = 0
registered_dni_csv = pd.read_csv("registeredDNI.csv")

for i in range(2):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camara {i} OK")
        camIndex=i
        #break
    else: 
        print(f"Camara {i} NO DISPONIBLE")


# Cola de eventos (OJO EL MAXSIZE)
frames = queue.Queue(maxsize=100)

# Cola para reconocer imagenes detectadas
detected = queue.Queue()


def camara_run(frames, duracion, show=True, camera_index=0):  #FALTA DECIDIR Y PROGRAMAR CUANTOS FRAMES SE VAN A GUARDAR EN LA COLA
    cap = cv2.VideoCapture(camera_index)  # Abre la cámara (ojo con el 0)

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


def detection_run():
    print("uenos dias")

def recognition_run():
    print("uenos tardes")

def run(frames, duracion):
    t_camera = threading.Thread(target=camara_run, args=(frames, duracion), daemon=True)
    t_detect = threading.Thread(target=detection_run, args=(), daemon=True)
    t_recognition = threading.Thread(target=recognition_run, args=(), daemon=True)

    t_camera.start(); t_detect.start(); t_recognition.start()



def registrar_foto(dfRegisteredWorkers):
    #devolvemos True si se ha registrado correctamente
    #devolvemos False si no se ha registrado (porque ha habido un Error o porque ya estaba registrado)

    cap = cv2.VideoCapture(i) #guarda en cap 
    ret, photo = cap.read()

    if (ret==False):
        print ("Error al leer frame")
        cap.release()
        return False
    
    cv2.imshow("Para guardar esta foto pulsa ENTER", photo)

    while(True):
        if (keyboard.read_key()=="enter"): 
            dni = input()
            if (dni not in dfRegisteredWorkers["DNI"].values):
                cv2.imwrite(f"/RegisteredPhotos/{dni}",photo)
                dfRegisteredWorkers.loc[len(dfRegisteredWorkers)] = [dni]
                dfRegisteredWorkers.to_csv("registeredDNI.csv", index=False)
                print(f"Trabajador {dni} registrado")
                cap.release()
                return True 
            else: #si ya esta registrado
                print("El trabajador ya está registrado")
                cap.release()
                return False 

            


# Flag para evitar que se ejecuten varias cosas a la vez
en_ejecucion = False


def ejecutar_registro():
    global en_ejecucion #global para poder cambiarlo para todo el main.py, no solo para esta función
    if en_ejecucion:
        print("Ya hay una acción en ejecución.")
        return
    #PONE EL "EN_EJECUCION" A TRUE PARA NO PODER EJECUTAR LA OTRA FUNCION (run) SI INTENTAMOS HACERLO
    en_ejecucion = True
    print("=== REGISTRANDO TRABAJADOR ===")
    registrar.registrar_foto(registered_dni_csv)
    en_ejecucion = False
    print("=== REGISTRO COMPLETADO ===")


def ejecutar_run():
    global en_ejecucion #global para poder cambiarlo para todo el main.py, no solo para esta función
    if en_ejecucion:
        print("Ya hay una acción en ejecución.")
        return
    #PONE EL "EN_EJECUCION" A TRUE PARA NO PODER EJECUTAR LA OTRA FUNCION (registro) SI INTENTAMOS HACERLO
    en_ejecucion = True
    print("=== INICIANDO RUN (10 segundos) ===")
    # Este RUN internamente crea 2 o 3 hilos (captura/detección/reconocimiento)
    run.run(frames, 10) #True o False es para abrir una ventana para los FRAMES
    en_ejecucion = False
    print("=== RUN COMPLETADO ===")


# Asignar callbacks simples y SIN HILOS
BTN_REGISTRAR.when_pressed = ejecutar_registro
BTN_RUN.when_pressed = ejecutar_run


# Loop principal — NO hay hilos aquí
while True:
    if keyboard.is_pressed("space"):
        break
    time.sleep(0.05)

""""
try:
    while True:
        evt = events.get()
        if evt == "UP":
            index = min(index + 1, len(freqs) - 1)
        elif evt == "DOWN":
            index = max(index - 1, 0)
        print(f"Frecuencia actual: {freqs[index]} Hz")
except KeyboardInterrupt:
    print("\nSaliendo...")
    led.off()
"""