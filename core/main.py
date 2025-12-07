import cv2
from gpiozero import Button, LED
import threading
import time
import pandas as pd
import os
import sys

# ✅ CONFIGURAR PATH (MUY IMPORTANTE)
# ========================================
# Obtener la ruta de ESTE archivo (core/main.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # /path/to/core/

# Obtener la ruta de la RAÍZ del proyecto (un nivel arriba)
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # /path/to/Facial_Recognition_Raspberry/

# Añadir la raíz al path para que Python encuentre tanto 'show' como 'core'
sys.path.insert(0, PROJECT_ROOT)

# ========================================
# ✅ IMPORTS (ahora todos funcionan)
# ========================================
import show  # ✅ Lo encuentra en la raíz

# ✅ Imports de core/ con ruta absoluta desde la raíz
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

BASE_PATH = PROJECT_ROOT  # Ya lo definiste arriba
registered_dni_csv = pd.read_csv(os.path.join(PROJECT_ROOT, "registeredDNI.csv"))

PATH_REGISTER= "/home/pi/Facial_Recognition_Raspberry/imagenes/registro/"
PATH_IMAGENES =f"/home/pi/Facial_Recognition_Raspberry/imagenes/frames/"

recognizer = None
names_labels = None

detection_thread = None
recognition_thread = None

frames = queue.frames


def find_camera_index(max_index):
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Cámara encontrada en el índice {i}")
            cap.release()
            return i
        cap.release()
    return None

camIndex = find_camera_index(4)
if camIndex is None:
    print("⚠️ ADVERTENCIA: No se detectó cámara al inicio.")
    camIndex = 0  # Valor por defecto

def run_camera(frames, duracion, path, name=None):
    t_camera = threading.Thread(target=camera.camara_run, args=(frames, duracion, path, camIndex, name))
    t_camera.start()
    return t_camera

def iniciar_hilos_permanentes():
    global detection_thread, recognition_thread
    
    # Solo crear hilos si no existen o están muertos
    if detection_thread is None or not detection_thread.is_alive():
        queue.stop_detection.clear()
        detection_thread = threading.Thread(target=detection.detection_run, daemon=True, name="DetectionThread")
        detection_thread.start()
        print("✅ Hilo de detección iniciado (permanente)")
    
    if recognition_thread is None or not recognition_thread.is_alive():
        queue.stop_recognition.clear()
        recognition_thread = threading.Thread(
            target=recognition.recognition_run,
            args=(recognizer, names_labels),
            daemon=True,
            name="RecognitionThread"
        )
        recognition_thread.start()
        print("✅ Hilo de reconocimiento iniciado (permanente)")

def limpiar_colas():
    cleared_frames = 0
    cleared_detected = 0
    
    while not queue.frames.empty():
        try:
            queue.frames.get_nowait()
            cleared_frames += 1
        except:
            break
    
    while not queue.detected.empty():
        try:
            queue.detected.get_nowait()
            cleared_detected += 1
        except:
            break
    
    if cleared_frames > 0 or cleared_detected > 0:
        print(f"🧹 Colas limpiadas: {cleared_frames} frames, {cleared_detected} detectados")


# Flag para evitar que se ejecuten varias cosas a la vez
en_ejecucion = False
ejecucion_lock = threading.Lock()


def ejecutar_registro():
    global en_ejecucion, recognizer, names_labels  # Importante: actualizar las variables globales

    with ejecucion_lock:
        if en_ejecucion:
            print("⚠️ Ya hay una acción en ejecución.")
            return
        en_ejecucion = True   #PONE EL "EN_EJECUCION" A TRUE PARA NO PODER EJECUTAR LA OTRA FUNCION (run) SI INTENTAMOS HACERLO
    try:
        print("\n" + "="*50)
        print("=== REGISTRANDO TRABAJADOR ===")
        print("\n" + "="*50)

        nombre_usuario = None
        while nombre_usuario is None or nombre_usuario.strip() == "":
            nombre_usuario = input("Introduce el nombre de usuario: ").strip()
            
            if not nombre_usuario:
                print("❌ El nombre no puede estar vacío. Intenta de nuevo.")
                continue
            
            # ✅ Verificar que no existe ya
            persona_path = os.path.join(PATH_REGISTER, nombre_usuario)
            if os.path.exists(persona_path):
                print(f"⚠️ El usuario '{nombre_usuario}' ya está registrado.")
                respuesta = input("¿Quieres reentrenar con nuevas fotos? (s/n): ").lower()
                if respuesta != 's':
                    nombre_usuario = None
                    continue
                else:
                    # Borrar las fotos antiguas
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
        
        with queue.model_lock:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(xml)
            names_labels = detection.namesToDictionary(PATH_REGISTER)

        iniciar_hilos_permanentes()
    finally:
        with ejecucion_lock:
            en_ejecucion = False



def ejecutar_run():
    global en_ejecucion

    with ejecucion_lock:
        if en_ejecucion:
            print("⚠️ Ya hay una acción en ejecución.")
            return
        en_ejecucion = True
    
    try:
        if recognizer is None or names_labels is None:
            print("❌ Modelo no cargado. Registra al menos una persona primero.")
            return
        
        print("=== INICIANDO RUN (10 segundos) ===")
        
        # ✅ Limpiar colas antes de capturar
        limpiar_colas()
        
        # ✅ Asegurar que los hilos están corriendo
        iniciar_hilos_permanentes()
        
        # ✅ Solo crear hilo de cámara (los otros ya están corriendo)
        t_camera = run_camera(frames, 10, PATH_IMAGENES)
        
        # ✅ Esperar a que termine la captura
        t_camera.join()
        
        print("=== RUN COMPLETADO ===")
        
        # ✅ Dar tiempo para procesar los últimos frames en las colas
        time.sleep(0.5)
        
    finally:
        with ejecucion_lock:
            en_ejecucion = False


# Asignar callbacks simples y SIN HILOS
BTN_REGISTRAR.when_pressed = ejecutar_registro
BTN_RUN.when_pressed = ejecutar_run

try:
    print("🚀 Sistema iniciado. Esperando botones...")
    print("   [BTN_REGISTRAR] - Registrar nueva persona")
    print("   [BTN_RUN] - Ejecutar reconocimiento\n")
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n🛑 Deteniendo sistema...")
    
    # Detener hilos de manera limpia
    queue.stop_detection.set()
    queue.stop_recognition.set()
    
    # Esperar a que terminen
    if detection_thread and detection_thread.is_alive():
        print("   Esperando hilo de detección...")
        detection_thread.join(timeout=2)
    if recognition_thread and recognition_thread.is_alive():
        print("   Esperando hilo de reconocimiento...")
        recognition_thread.join(timeout=2)
    
    print("✅ Saliendo...")
    led.off()