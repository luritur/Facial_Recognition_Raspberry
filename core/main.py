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
from config import LED_PIN, BTN_DETENER, led, camIndex, PATH_REGISTER, MODEL_PATH





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


def run_camera_thread(duracion, path=None, queue_frames = None, camera_index=None, dni=None):
    """
    Lanza el hilo de la cámara. Si no se pasa `camera_index`, usa el `camIndex` detectado.
    """
    idx = camera_index if camera_index is not None else camIndex
    t_camera = threading.Thread(target=camera.camara_run, args=(queue_frames, duracion, path, idx, dni))
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
    global en_ejecucion
    try:
        control.entrenamiento_progreso = 0
        control.entrenamiento_mensaje = "Iniciando entrenamiento..."
        print("🔄 Entrenando modelo...")
        
        control.entrenamiento_progreso = 20
        control.entrenamiento_mensaje = "Cargando imágenes de empleados..."
        time.sleep(0.1)  # Pequeña pausa para que se vea el progreso
        
        config.xml = train.trainLBPH(PATH_REGISTER)
        
        control.entrenamiento_progreso = 70
        control.entrenamiento_mensaje = "Creando modelo de reconocimiento..."
        time.sleep(0.1)
        
        config.recognizer = cv2.face.LBPHFaceRecognizer_create()
        config.recognizer.read(config.xml)
        config.names_labels = detection.namesToDictionary(PATH_REGISTER)
        
        control.entrenamiento_progreso = 100
        control.entrenamiento_mensaje = "¡Entrenamiento completado!"

        if(en_ejecucion): #cuando se entrena el modelo, si el reconocimiento se estaba ejecutando, se detiene y se vuelve a ejecutar con el nuevo modelo
            print("⏸️ Pausando reconocimiento/acción en curso para reanudar con el nuevo modelo..")
            detener_run()
            # Esperar un poco a que los hilos terminen y la cámara quede libre
            wait_start = time.time()
            while hilos_activos:
                if time.time() - wait_start > 6:
                    print("⚠️ Tiempo de espera por liberación de hilos excedido, continuando de todas formas")
                    break
                time.sleep(0.1)
            time.sleep(0.2)

            stop_event.clear()  # Limpiar stop_event al inicio
            print("▶️ Reanudando reconocimiento con el nuevo modelo...")
            ejecutar_run()
        
        print(f"✅ MODELO ENTRENADO CON TODOS LOS EMPLEADOS: {config.names_labels}")
        print("=== REGISTRO COMPLETADO ===\n")
        
        # Mantener el mensaje de completado por 2 segundos
        time.sleep(2)
        
    except Exception as e:
        control.entrenamiento_progreso = -1
        control.entrenamiento_mensaje = f"Error: {str(e)}"
        print(f"❌ Error en entrenamiento: {e}")
    finally:
        control.entrenando_modelo = False


en_ejecucion = False

def ejecutar_registro(nombre_empleado, dni, email, jornada):
    global en_ejecucion
    # Detectar si había reconocimiento / detección en marcha
    reconocimiento_ejecutandose = bool(getattr(run_recognition_thread, "started", False) or getattr(run_detect_thread, "started", False) or en_ejecucion)

    if reconocimiento_ejecutandose:
        print("⏸️ Pausando reconocimiento/acción en curso para realizar registro...")
        detener_run()
        # Esperar un poco a que los hilos terminen y la cámara quede libre
        wait_start = time.time()
        while hilos_activos:
            if time.time() - wait_start > 6:
                print("⚠️ Tiempo de espera por liberación de hilos excedido, continuando de todas formas")
                break
            time.sleep(0.1)
        time.sleep(0.2)
        en_ejecucion = False

    en_ejecucion = True
    stop_event.clear()  # Limpiar stop_event al inicio

    # usar camIndex detectado por defecto
    rc = run_camera_thread(8, PATH_REGISTER, camera_index=camIndex, dni=dni)

    rc.join()
    
    if stop_event.is_set():
        print("🛑 Registro cancelado por señal")
        en_ejecucion = False
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
    if reconocimiento_ejecutandose:
        time.sleep(0.2)
        print("▶️ Reanudando reconocimiento después del registro...")
        ejecutar_run()

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
    
    run_camera_thread(1, queue_frames=frames)
    #def run_camera_thread(duracion, path=None, quee_frames = None, camera_index=None, dni=None):

    run_detect_thread()
    run_recognition_thread(config.recognizer, config.names_labels)
    
    print("\n=== RUN INICIADO (se liberará automáticamente en 12 segundos) ===\n")
    return True #para ver si se ha iniciado correctamente ---> para el error en el reconocimiento si no hay nadie registrado

def detener_run():
    global hilos_activos, en_ejecucion
    stop_event.set()  # activamos el flag para parar los hilos (camara, deteccion y reconocimiento)

    # Iterar sobre una copia para poder hacer join y eliminar de la lista sin modificar
    for t in hilos_activos[:]:
        try:
            t.join(timeout=5)  # timeout para no bloquear indefinidamente
        except Exception as e:
            print(f"[detener_run] Error al hacer join(): {e}")
        try:
            hilos_activos.remove(t)
        except ValueError:
            pass

    en_ejecucion = False
    # borramos contenido de las colas
    queue.clear_queues()
    run_detect_thread.started = False
    run_recognition_thread.started = False
    print("✅ Reconocimiento detenido de forma segura")
# ========================================
# ASIGNAR CALLBACKS
# ========================================

BTN_DETENER.when_pressed = detener_run

# ========================================
# LOOP PRINCIPAL
# ========================================
try:
    if IS_RASPBERRY:
        print("\n✅ Sistema iniciado - Esperando botones físicos...")

    else:
        print("\n✅ Sistema iniciado - Modo simulación Windows")

        

except KeyboardInterrupt:
    print("\n\n👋 Saliendo...")
    led.off()