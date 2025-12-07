import cv2
from gpiozero import Button, LED
import threading
import time
import pandas as pd
import os
import sys

# CONFIGURAR PATH (MUY IMPORTANTE)
# ========================================
# Obtener la ruta de ESTE archivo (core/main.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # /path/to/core/

# Obtener la ruta de la RAIZ del proyecto (un nivel arriba)
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # /path/to/Facial_Recognition_Raspberry/

# Añadir la rai­z al path para que Python encuentre tanto 'show' como 'core'
sys.path.insert(0, PROJECT_ROOT)

# ========================================
# IMPORTS (ahora todos funcionan)
# ========================================
import show  # Lo encuentra en la rai­z

# Imports de core/ con ruta absoluta desde la rai­z
import core.detection.detection as detection
import core.recognition.recognition as recognition
import core.camera.camera as camera
import core.queues.queue_class as queue 
import core.recognition.train_LBPH as train



import core.detection.detection as detection
import core.recognition.recognition as recognition
import core.camera.camera as camera
import core.queues.queue_class as queue 
import core.recognition.train_LBPH as train

# Pines BCM
LED_PIN = 17
BTN_RUN = Button(24, pull_up=True)  # disminuye frecuencia
BTN_REGISTRAR = Button(23, pull_up=True)    # aumenta frecuencia
led = LED(LED_PIN)
camIndex = 0

BASE_PATH = PROJECT_ROOT  # Ya lo definiste arriba
registered_dni_csv = pd.read_csv(os.path.join(PROJECT_ROOT, "registeredDNI.csv"))

PATH_REGISTER= "/home/pi/Facial_Recognition_Raspberry/imagenes/registro/"
PATH_IMAGENES =f"/home/pi/Facial_Recognition_Raspberry/imagenes/frames/"

recognizer = None
names_labels = None

frames = queue.frames


def find_camera_index(max_index):
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camara encontrada en el indice {i}")
            cap.release()
            return i
        cap.release()
    return None

camIndex = find_camera_index(4)
if camIndex is None:
    print("ADVERTENCIA: No se detecta camara al inicio.")
    print("Se intentara abrir la camara cuando ejecutes registro/run.")
    camIndex = 0  # Valor por defecto

def run_camera(frames, duracion, path, name=None):
    t_camera = threading.Thread(target=camera.camara_run, args=(frames, duracion, path, camIndex, name))
    t_camera.start()
    return t_camera

def run_detect_thread():
    # Solo lanzar detection si no existe ya
    if not getattr(run_detect_thread, "started", False):
        t_detect = threading.Thread(target=detection.detection_run, daemon=True)
        t_detect.start()
        run_detect_thread.started = True
        print("Hilo de deteccion iniciado")


def run_recognition_thread(recognizer, names_labels):
    # Solo lanzar recognition si no existe ya
    if not getattr(run_recognition_thread, "started", False):
        t_recognition = threading.Thread(target=recognition.recognition_run,
                                         args=(recognizer, names_labels),
                                         daemon=True)
        t_recognition.start()
        run_recognition_thread.started = True
        print("Hilo de reconocimiento iniciado")

def run_show_video(): 
    t_video = threading.Thread(target=show.show_video_run, args=(), daemon=True)
    t_video.start(); 

"""
def test_camara():
    print("=== TEST DE CAMARA ===")
    camara_run(frames=queue.Queue(), duracion=5, camera_index=camIndex,)
    print("=== FIN DEL TEST ===")
"""


# Flag para evitar que se ejecuten varias cosas a la vez
en_ejecucion = False


def ejecutar_registro():
    global en_ejecucion, recognizer, names_labels  # Importante: actualizar las variables globales

    if en_ejecucion:
        print("Ya hay una accion en ejecucion.")
        return
    
    #PONE EL "EN_EJECUCION" A TRUE PARA NO PODER EJECUTAR LA OTRA FUNCION (run) SI INTENTAMOS HACERLO
    en_ejecucion = True
    print("\n" + "="*50) 
    print("=== REGISTRANDO TRABAJADOR ===") 
    print("\n" + "="*50) 
    nombre_usuario = None 
    while nombre_usuario is None or nombre_usuario.strip() == "":
        nombre_usuario = input("Introduce el nombre de usuario: ").strip()
        if not nombre_usuario: 
            print("❌ El nombre no puede estar vacío. Intenta de nuevo.") 
            continue # ✅ Verificar que no existe ya 
        persona_path = os.path.join(PATH_REGISTER, nombre_usuario) 
        if os.path.exists(persona_path): 
            print(f"⚠️ El usuario '{nombre_usuario}' ya está registrado.") 
            respuesta = input("¿Quieres reentrenar con nuevas fotos? (s/n): ").lower()
            if respuesta != 's': 
                nombre_usuario = None 
                continue 
            else: # Borrar las fotos antiguas 
                import shutil 
                shutil.rmtree(persona_path) 
                print(f"🗑️ Fotos antiguas de '{nombre_usuario}' eliminadas") 
                break 
        break 
    print(f"\n✅ Registrando usuario: {nombre_usuario}") 
    print("📸 Prepárate... Captura en 3 segundos\n") 
    rc=run_camera(frames, 3, PATH_REGISTER, nombre_usuario)#registramos el usuario JohnPork de prueba 
    rc.join() 
    persona_path = os.path.join(PATH_REGISTER, nombre_usuario) 
    if not os.path.exists(persona_path) or len(os.listdir(persona_path)) == 0: 
        print("❌ ERROR: No se capturaron imágenes. Verifica la cámara.")
        return 
    num_fotos = len(os.listdir(persona_path)) 
    print(f"✅ Se capturaron {num_fotos} imágenes de {nombre_usuario}")
    print("=== REGISTRO COMPLETADO ===")

    xml = train.trainLBPH(PATH_REGISTER) #cada vez que registremos una persona nueva hay que entrenar el modelo con esa persona nueva
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(xml)
    names_labels = detection.namesToDictionary(PATH_REGISTER)

    en_ejecucion = False



def ejecutar_run():
    global en_ejecucion, recognizer, names_labels

    if en_ejecucion:
        print("Ya hay una accion en ejecucion.")
        return
    
    if recognizer is None or names_labels is None:
        print("Modelo no cargado. Registra al menos una persona primero.")
        return
    
    #PONE EL "EN_EJECUCION" A TRUE PARA NO PODER EJECUTAR LA OTRA FUNCION (registro) SI INTENTAMOS HACERLO
    en_ejecucion = True
    print("=== INICIANDO RUN (10 segundos) ===")
    # Este RUN internamente crea 2 o 3 hilos (captura/detecciÃ³n/reconocimiento)
    run_camera(frames, 10, PATH_IMAGENES)
    run_detect_thread()
    run_recognition_thread(recognizer, names_labels)
    #run_show_video() 

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

