import cv2
from gpiozero import Button, LED
import threading
import time
import pandas as pd
import os


import show
#import keyboard


import detection
import recognition
import camera
import queue_class as queue 

# Pines BCM
LED_PIN = 17
BTN_REGISTRAR = Button(23, pull_up=True)    # aumenta frecuencia
BTN_RUN = Button(24, pull_up=True)  # disminuye frecuencia
led = LED(LED_PIN)
camIndex = 0
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
registered_dni_csv = pd.read_csv(os.path.join(BASE_PATH, "registeredDNI.csv"))

frames = queue.frames


for i in range(2):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camara {i} OK")
        camIndex=i
        #break
    else: 
        print(f"Camara {i} NO DISPONIBLE")




def run_camera(frames, duracion, path):
    t_camera = threading.Thread(target=camera.camara_run, args=(frames, duracion, path, camIndex), daemon=True)
    t_camera.start()

def run_detect_thread():
    t_detect = threading.Thread(target=detection.detection_run, args=(), daemon=True)
    t_detect.start()

def run_recognition_thread():
    t_recognition = threading.Thread(target=recognition.recognition_run, args=(), daemon=True)
    t_recognition.start()

def run_show_video(): 
    t_video = threading.Thread(target=show.show_video_run, args=(), daemon=True)
    t_video.start(); 

"""
def test_camara():
    print("=== TEST DE CÁMARA ===")
    camara_run(frames=queue.Queue(), duracion=5, camera_index=camIndex,)
    print("=== FIN DEL TEST ===")
"""


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
    path =f"/home/pi/Facial_Recognition_Raspberry/imagenes/registro/"

    run_camera(frames, 3, path)
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
    path =f"/home/pi/Facial_Recognition_Raspberry/imagenes/frames/"
    run_camera(frames, 10, path)
    run_detect_thread()
    run_recognition_thread()
    run_show_video() 

    #test_camara()
    en_ejecucion = False
    print("=== RUN COMPLETADO ===")


# Asignar callbacks simples y SIN HILOS
BTN_REGISTRAR.when_pressed = ejecutar_registro
BTN_RUN.when_pressed = ejecutar_run
# ...existing code...
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Saliendo...")
    led.off()

