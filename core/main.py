import cv2
from gpiozero import Button, LED
import threading
import time
import pandas as pd
import os


import show
#import keyboard


import core.detection.detection as detection
import core.recognition.recognition as recognition
import core.camera.camera as camera
import core.queues.queue_class as queue 
import core.recognition.train_LBPH as train

# Pines BCM
LED_PIN = 17
BTN_REGISTRAR = Button(23, pull_up=True)    # aumenta frecuencia
BTN_RUN = Button(24, pull_up=True)  # disminuye frecuencia
led = LED(LED_PIN)
camIndex = 0
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
registered_dni_csv = pd.read_csv(os.path.join(BASE_PATH, "registeredDNI.csv"))

PATH_REGISTER= "/home/pi/Facial_Recognition_Raspberry/imagenes/registro/"
PATH_IMAGENES =f"/home/pi/Facial_Recognition_Raspberry/imagenes/frames/"

recognizer = None
names_labels = None

frames = queue.frames


for i in range(2):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camara {i} OK")
        camIndex=i
        #break
    else: 
        print(f"Camara {i} NO DISPONIBLE")




def run_camera(frames, duracion, path, name=None):
    t_camera = threading.Thread(target=camera.camara_run, args=(frames, duracion, path, camIndex, name))
    t_camera.start()
    return t_camera

def run_detect_thread():
    t_detect = threading.Thread(target=detection.detection_run, args=(), daemon=True)
    t_detect.start()


def run_recognition_thread(recognizer, names_labels):
    t_recognition = threading.Thread(target=recognition.recognition_run, args=(recognizer, names_labels), daemon=True)
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
    global en_ejecucion, recognizer, names_labels  # Importante: actualizar las variables globales

    if en_ejecucion:
        print("Ya hay una acción en ejecución.")
        return
    #PONE EL "EN_EJECUCION" A TRUE PARA NO PODER EJECUTAR LA OTRA FUNCION (run) SI INTENTAMOS HACERLO
    en_ejecucion = True
    print("=== REGISTRANDO TRABAJADOR ===")

    rc=run_camera(frames, 3, PATH_REGISTER, "JohnPork")#registramos el usuario JohnPork de prueba
    rc.join()
    print("=== REGISTRO COMPLETADO ===")
    xml = train.trainLBPH(PATH_REGISTER) #cada vez que registremos una persona nueva hay que entrenar el modelo con esa persona nueva
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(xml)
    names_labels = detection.namesToDictionary(PATH_REGISTER)

    en_ejecucion = False



def ejecutar_run():
    global en_ejecucion, recognizer, names_labels
    if en_ejecucion:
        print("Ya hay una acción en ejecución.")
        return
    
    if recognizer is None or names_labels is None:
        print("Modelo no cargado. Registra al menos una persona primero.")
        return
    
    #PONE EL "EN_EJECUCION" A TRUE PARA NO PODER EJECUTAR LA OTRA FUNCION (registro) SI INTENTAMOS HACERLO
    en_ejecucion = True
    print("=== INICIANDO RUN (10 segundos) ===")
    # Este RUN internamente crea 2 o 3 hilos (captura/detección/reconocimiento)
    run_camera(frames, 10, PATH_IMAGENES)
    run_detect_thread()
    run_recognition_thread(recognizer, names_labels)
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

