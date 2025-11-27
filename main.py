import glob
import cv2
from gpiozero import Button, LED
import threading
import time
import csv
import pandas as pd
import os
import shutil
import detection as detect
import queue_class as queue
#import keyboard

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


def borrar_contenido_carpeta(ruta):
    # Borra todo el contenido de la carpeta, incluyendo subcarpetas y archivos
    for nombre in os.listdir(ruta):
        path = os.path.join(ruta, nombre)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

def camara_run(frames, duracion,path, camera_index=camIndex):  #FALTA DECIDIR Y PROGRAMAR CUANTOS FRAMES SE VAN A GUARDAR EN LA COLA
    cap = cv2.VideoCapture(camera_index)  # Abre la cámara (ojo con el 0)
    borrar_contenido_carpeta("/home/pi/Facial_Recognition_Raspberry/imagenes/frames/")

    print(f"run.py: captura iniciada durante {duracion} segundos")
    inicio = time.time()
    frames_put=0
    #frame_guardado = False   # Para guardar solo un frame
    if("frames" in path):#lanzamos hilo de detectar
        run_detect()
        print("detectando........")

    while time.time() - inicio < duracion: #x segundos de while (se pasa como parametro)
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer el frame.")
            break
        frames.put(frame)


        frames_put+=1

        ruta = f"{path}frame{frames_put}.jpg"
        cv2.imwrite(ruta, frame)
        print(f"Frame guardado en: {ruta}")


    cap.release()

"""
def test_camara():
    print("=== TEST DE CÁMARA ===")
    camara_run(frames=queue.Queue(), duracion=5, camera_index=camIndex,)
    print("=== FIN DEL TEST ===")
"""



def recognition_run():
    print("uenos tardes")
    #aqui hacer eigenfaces recognition


def run_detect():
    t_detect = threading.Thread(target=detect.detection_run, args=(), daemon=True)
    t_detect.start()

def run_camera(frames, duracion, path):
    t_camera = threading.Thread(target=camara_run, args=(frames, duracion, path), daemon=True)
    t_camera.start(); 


            


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

