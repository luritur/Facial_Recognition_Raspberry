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
from core.bd.bd_functions import actualizar_empleado 
from flask import current_app

frames = queue.detected
THRESHOLD = 85  # Ajusta según los resultados que veas

# Guardamos cuando se ha reconocido a cada persona para evitar que se reconozca muchas veces en el mismo segundo
estado_empleados = {}          
ultimo_timestamp = {}          
TIEMPO_MINIMO = 10

def recognition_run(recognizer, names_labels, app=None):
    """
    :param app: Instancia de la aplicación Flask (necesaria para el contexto)
    """
    # Si no se pasa app, intentar obtenerla del current_app
    if app is None:
        try:
            app = current_app._get_current_object()
        except RuntimeError:
            print("ERROR: No se puede obtener app. Debes pasar la instancia de Flask al hilo.")
            return
    
    label_name = {value: key for key, value in names_labels.items()}
    print("reconociendo...")
    print(f"Personas registradas: {label_name}")
    
    while not stop_event.is_set():
        ahora = time.time()

        # Coger el frame de la cola frames 
        face_gray = queue.detected.get() 
        
        # Redimensionar para consistencia (IMPORTANTE)
        face_resized = cv2.resize(face_gray, (100, 100))

        # Recognize the face using the trained model
        label, confidence = recognizer.predict(face_resized)

        # Si nunca ha sido visto antes:
        if label_name[label] not in ultimo_timestamp:
            ultimo_timestamp[label_name[label]] = 0

        # Evitar duplicados en un corto intervalo
        if ahora - ultimo_timestamp[label_name[label]] < TIEMPO_MINIMO:
            continue

        ultimo_timestamp[label_name[label]] = ahora

        # DEBUG: Imprimir SIEMPRE los valores
        print(f"Label: {label_name[label]}, Confidence: {confidence:.2f}")
        
        if confidence < THRESHOLD:  
            dni = label_name[label]
            estado_actual = estado_empleados.get(dni, "out")

            if estado_actual == "out":
                # Cambia OUT → WORKING
                nuevo_estado = "trabajando"
                estado_empleados[dni] = "trabajando"
            elif estado_actual == "trabajando":
                # Cambia WORKING → OUT
                nuevo_estado = "out"
                estado_empleados[dni] = "out"
            
            # IMPORTANTE: Usar app_context dentro del hilo
            with app.app_context():
                if actualizar_empleado(dni=dni, estado=nuevo_estado):
                    registrar_reconocimiento(dni, confidence)
                    notificar_empleado_actualizado(dni, nuevo_estado)
                    print(f"✅ Reconocido: {dni} - Nuevo estado: {nuevo_estado}")
                else:
                    print(f"❌ Error al actualizar estado en BD para {dni}")
        else:
            print('❌ No se ha reconocido al usuario')



            






# RECOGNIZE faces: 
    #1. detectar cara con detection.py del frame que llega 
    #2. pasarlo a grayScale 
    #3. detectar usando el modelo entrenado .xml