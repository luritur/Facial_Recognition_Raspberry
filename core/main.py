import cv2
import threading
import time
import pandas as pd
import os
import sys
import platform

import core.show as show
import core.detection.detection as detection
import core.recognition.recognition as recognition
import core.camera.camera as camera
import core.queues.colas as queue 
import core.recognition.train_LBPH as train

from core.control import hilos_activos
from core.control import stop_event
import core.control as control

import config
from core.gestion.gestion_empleados import notificar_empleado_actualizado, notificar_nuevo_empleado

from core.bd.bd_functions import actualizar_empleado, agregar_empleado, obtener_empleados_lista, empleado_exist
# ========================================
# DETECCIÓN DE PLATAFORMA
# ========================================
IS_RASPBERRY = platform.machine().startswith('arm') or platform.machine().startswith('aarch')

# Importar GPIO solo en Raspberry Pi
if IS_RASPBERRY:
    from gpiozero import Button, LED
    print("🔧 Modo Raspberry Pi detectado - GPIO habilitado")
else:
    print("💻 Modo Windows/PC detectado - Simulando GPIO con teclado")
    # Clase simulada para LED
    class LED:
        def __init__(self, pin):
            self.pin = pin
            self.state = False
        
        def on(self):
            self.state = True
            print(f"💡 LED {self.pin} encendido")
        
        def off(self):
            self.state = False
            print(f"💡 LED {self.pin} apagado")
    
    # Clase simulada para Button
    class Button:
        def __init__(self, pin, pull_up=True):
            self.pin = pin
            self.when_pressed = None
        
        def _trigger(self):
            if self.when_pressed:
                self.when_pressed()


# ========================================
# IMPORTAR CONFIGURACIÓN GLOBAL
# ========================================
from config import LED_PIN, BTN_RUN, BTN_REGISTRAR, led, camIndex, PATH_REGISTER, PATH_IMAGENES, MODEL_PATH





frames = queue.frames
# ========================================
# FUNCIONES
# ========================================
def find_camera_index(max_index):
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"📷 Cámara encontrada en el índice {i}")
            cap.release()
            return i
        cap.release()
    return None

camIndex = find_camera_index(4)
if camIndex is None:
    print("⚠️ ADVERTENCIA: No se detecta cámara al inicio.")
    print("Se intentará abrir la cámara cuando ejecutes registro/run.")
    camIndex = 0


def run_camera_thread(frames, duracion, path, dni=None):
    t_camera = threading.Thread(target=camera.camara_run, args=(frames, duracion, path, 0, dni))
    t_camera.start()
    hilos_activos.append(t_camera)
    return t_camera

def run_detect_thread():
    if not getattr(run_detect_thread, "started", False):
        t_detect = threading.Thread(target=detection.detection_run, daemon=True)
        t_detect.start()
        run_detect_thread.started = True
        #print("🔍 Hilo de detección iniciado")
        hilos_activos.append(t_detect)

    

def run_recognition_thread(recognizer, names_labels):
    if not getattr(run_recognition_thread, "started", False):
        t_recognition = threading.Thread(target=recognition.recognition_run,
                                         args=(recognizer, names_labels),
                                         daemon=True)
        t_recognition.start()
        run_recognition_thread.started = True
        #print("👤 Hilo de reconocimiento iniciado")
        hilos_activos.append(t_recognition)



def run_entrenar_modelo_thread():

    if control.entrenando_modelo: 
        print("Entrenamiento ya en curso, no inicie otro")
        return 
    
    control.entrenando_modelo = True
    t_entrenar_modelo = threading.Thread(target=train_model,daemon=True)
    t_entrenar_modelo.start()
    hilos_activos.append(t_entrenar_modelo)

        

def train_model():
    print("🔄 Entrenando modelo...")
    
    config.xml = train.trainLBPH(PATH_REGISTER)
    
    config.recognizer = cv2.face.LBPHFaceRecognizer_create()
    config.recognizer.read(config.xml)
    config.names_labels = detection.namesToDictionary(PATH_REGISTER) 
    control.entrenando_modelo = False

    print(f"MODELO ENTRENADO CON TODOS LOS EMPLEADOS: {config.names_labels}")
    print("=== REGISTRO COMPLETADO ===\n")


en_ejecucion = False

def ejecutar_registro(nombre_empleado, dni, email, jornada):
    global en_ejecucion

    if en_ejecucion:
        print("⚠️ Ya hay una acción en ejecución.")
        return
    
    en_ejecucion = True
    if stop_event.is_set():
        print("🛑 Cámara detenido por señal")
        return 
        
    rc = run_camera_thread(frames, 8, PATH_REGISTER, dni)
    rc.join() 
    
    if stop_event.is_set():
        print("🛑 Cámara detenido por señal")
        return 
    persona_path = os.path.join(PATH_REGISTER, dni) 
    if not os.path.exists(persona_path) or len(os.listdir(persona_path)) == 0: 
        print("❌ ERROR: No se capturaron imágenes. Verifica la cámara.")
        en_ejecucion = False
        return 
    if empleado_exist(dni): 
        print("❌ EL EMPLEADO YA EXISTE")
        en_ejecucion = False
        return 
    
    print("llamando a notificar_empleado")
    notificar_nuevo_empleado(dni, nombre_empleado, email, jornada)
    agregar_empleado(dni, nombre_empleado,email, jornada, persona_path)

    print("llamada a notificar_empleado HECHAAA")

    num_fotos = len(os.listdir(persona_path)) 
    print(f"Se capturaron {num_fotos} imágenes de {nombre_empleado} DNI:{dni}")
    print(f"✅ Registro completado para:{nombre_empleado} DNI:{dni} ")
    en_ejecucion = False

def ejecutar_run():

    global en_ejecucion
    stop_event.clear()
    if en_ejecucion:
        print("⚠️ Ya hay una acción en ejecución.")
        return
    
    # VERIFICAR SI EL ARCHIVO XML FUE ELIMINADO
    if not os.path.exists(MODEL_PATH):
        config.recognizer = None
        config.names_labels = None
        config.xml = None
        print("⚠️ No existe ningun modelo")
    
    if config.recognizer is None or config.names_labels is None:
        print("❌ Modelo no cargado. Registra al menos una persona primero.")
        return
    
    en_ejecucion = True
    print("\n" + "="*50)
    print("=== INICIANDO RUN (10 segundos) ===")
    print("="*50 + "\n")
    
    run_camera_thread(frames, 10, PATH_IMAGENES)
    run_detect_thread()
    run_recognition_thread(config.recognizer, config.names_labels)
    
    en_ejecucion = False
    print("\n=== RUN COMPLETADO ===\n")

def detener_run():
    global hilos_activos, en_ejecucion
    stop_event.set() #activamos el flag para parar los hilos (camara, deteccion y reconocimiento)
    for t in hilos_activos: 
        t.join()       # Espera a que cada hilo termine correctamente
        hilos_activos.remove(t)
    en_ejecucion = False
    #borramos contenido de las colas
    queue.clear_queues()
    run_detect_thread.started = False
    run_recognition_thread.started = False
        

    print("✅ Reconocimiento detenido de forma segura")
# ========================================
# ASIGNAR CALLBACKS
# ========================================
BTN_REGISTRAR.when_pressed = ejecutar_registro
BTN_RUN.when_pressed = ejecutar_run

# ========================================
# LOOP PRINCIPAL
# ========================================
try:
    if IS_RASPBERRY:
        print("\n✅ Sistema iniciado - Esperando botones físicos...")
        print("📌 BTN_REGISTRAR (GPIO 23) - Registrar nuevo usuario")
        print("📌 BTN_RUN (GPIO 24) - Iniciar reconocimiento")
        print("Presiona Ctrl+C para salir\n")
        while True:
            time.sleep(0.1)
    else:
        print("\n✅ Sistema iniciado - Modo simulación Windows")
        print("="*50)
        print("CONTROLES DE TECLADO:")
        print("  1 - Registrar nuevo usuario")
        print("  2 - Iniciar reconocimiento (RUN)")
        print("  q - Salir")
        print("="*50 + "\n")
        

except KeyboardInterrupt:
    print("\n\n👋 Saliendo...")
    led.off()