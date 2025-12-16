#con LBPH: https://www.geeksforgeeks.org/computer-vision/face-recognition-with-local-binary-patterns-lbps-and-opencv/?utm_source=chatgpt.com

import cv2
import os
import numpy as np
import core.queues.colas as queue
import core.detection.detection as detection 
from core.control import stop_event
from core.gestion.gestion_empleados import registrar_reconocimiento
import time
from core.gestion.gestion_empleados import notificar_empleado_actualizado
from core.bd.bd_functions import registrar_entrada_empleado, registrar_salida_empleado, obtener_empleados_lista
from config import led

frames = queue.detected
THRESHOLD = 85  # Ajusta según los resultados que veas

# Guardamos cuando se ha reconocido a cada persona para evitar reconocimientos duplicados
ultimo_timestamp = {}          
TIEMPO_MINIMO = 10  # Segundos mínimos entre reconocimientos del mismo empleado

def recognition_run(recognizer, names_labels):
    """
    Ejecuta el loop de reconocimiento facial.
    Detecta entrada/salida de empleados y calcula tiempo trabajado.
    """
    label_name = {value: key for key, value in names_labels.items()}  # Invertir diccionario
    print("🔍 Reconociendo...")
    print(f"👥 Personas registradas: {label_name}")
    
    while not stop_event.is_set():
        ahora = time.time()

        # Obtener frame de la cola
        face_gray = queue.detected.get() 
        face_resized = cv2.resize(face_gray, (100, 100))

        # Reconocer rostro usando el modelo entrenado
        label, confidence = recognizer.predict(face_resized)
        
        dni = label_name[label]

        # Inicializar timestamp si es la primera vez
        if dni not in ultimo_timestamp:
            ultimo_timestamp[dni] = 0

        # Evitar duplicados en corto intervalo
        if ahora - ultimo_timestamp[dni] < TIEMPO_MINIMO:
            continue

        ultimo_timestamp[dni] = ahora

        # Debug: imprimir siempre los valores
        print(f"🎯 Label: {dni}, Confidence: {confidence:.2f}")
        
        # Solo procesar si la confianza es suficiente
        if confidence < THRESHOLD:  
            # Obtener empleado actual de la BD
            empleados = obtener_empleados_lista()
            empleado = None
            for emp in empleados:
                if emp.dni == dni:
                    empleado = emp
                    break
            
            if not empleado:
                print(f"⚠️ Empleado {dni} no encontrado en BD")
                continue
            
            estado_actual = empleado.estado
            
            print(f"✅ Reconocido: {empleado.nombre} (DNI: {dni})")
            print(f"📊 Estado actual: {estado_actual}")
            
            # Lógica de entrada/salida
            if estado_actual == 'out' or estado_actual == 'completado':
                # ENTRADA - Iniciar sesión de trabajo
                print(f"🟢 ENTRADA registrada para {empleado.nombre}")
                resultado = registrar_entrada_empleado(dni)
                nuevo_estado = 'working'
                
                # Feedback LED
                led.on()
                time.sleep(0.3)
                led.off()
                
            elif estado_actual == 'working':
                # SALIDA - Finalizar sesión de trabajo
                print(f"🔴 SALIDA registrada para {empleado.nombre}")
                resultado = registrar_salida_empleado(dni)
                
                # Obtener estado actualizado después de calcular jornada
                empleados_updated = obtener_empleados_lista()
                for emp in empleados_updated:
                    if emp.dni == dni:
                        nuevo_estado = emp.estado
                        break
                
                # Feedback LED (doble parpadeo para salida)
                led.on()
                time.sleep(0.2)
                led.off()
                time.sleep(0.2)
                led.on()
                time.sleep(0.2)
                led.off()
            else:
                print(f"⚠️ Estado desconocido: {estado_actual}")
                continue
            
            # Registrar reconocimiento para el sistema
            registrar_reconocimiento(dni, confidence)
            
            # Notificar cambio a la interfaz web
            notificar_empleado_actualizado(dni, nuevo_estado)
            
            print(f"🔄 Cambio completado: {estado_actual} → {nuevo_estado}")
            print("=" * 60)
        else:
            print(f"❌ Confianza insuficiente: {confidence:.2f} (umbral: {THRESHOLD})")



            






# RECOGNIZE faces: 
    #1. detectar cara con detection.py del frame que llega 
    #2. pasarlo a grayScale 
    #3. detectar usando el modelo entrenado .xml