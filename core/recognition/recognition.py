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
from core.bd.bd_functions import actualizar_estado_empleado
from config import led
frames = queue.detected
THRESHOLD = 85  # Ajusta segun los resultados que veas

#guardamos cuando se ha reconocido a cada persona para evitar que se reconozca muchas veces en el mismo segundo (q solo cambie de estado cuando tenga sentido)
estado_empleados = {}          
ultimo_timestamp = {}          
TIEMPO_MINIMO = 10

def recognition_run(recognizer, names_labels): #OJOJO como hacer para cerrar el bucle
    label_name = {value: key for key, value in names_labels.items()} #invertir el diccionario
    print("reconociendo...")
    print(f"Personas registradas: {label_name}")
    while not stop_event.is_set():
        ahora = time.time()

        #coger el frame de la cola frames 
        #reconocer el frame 
        face_gray = queue.detected.get() 
        # 2. Redimensionar para consistencia (IMPORTANTE)
        face_resized = cv2.resize(face_gray, (100, 100))  # âñADIDO

        # Recognize and label the faces
         # Recognize the face using the trained model
        label, confidence = recognizer.predict(face_resized)

        # Si nunca ha sido visto antes:
        if label_name[label] not in ultimo_timestamp:
            ultimo_timestamp[label_name[label]] = 0

        # Evitar duplicados en un corto intervalo
        if ahora - ultimo_timestamp[label_name[label]] < TIEMPO_MINIMO:
            continue

        ultimo_timestamp[label_name[label]] = ahora

        # 4. DEBUG: Imprimir SIEMPRE los valores
        print(f"Label: {label_name[label]}, Confidence: {confidence:.2f}")   #(para ver los thresholds y poder cambiar luego el if)
        #print(confidence)
        if confidence < THRESHOLD:  
            dni = label_name[label]
            estado_actual = estado_empleados.get(dni, "out")

            if estado_actual == "out":
                nuevo_estado = "working"
            elif estado_actual == "working":
                nuevo_estado = "out"
            else:
                nuevo_estado = "working"  # Por si acaso
            estado_empleados[dni] = nuevo_estado
            
            print(f"✅ Se ha reconocido al usuario: {dni}")
            led.on()
            time.sleep(0.5)
            led.off()
            print(f"🔄 Cambiando estado: {estado_actual} → {nuevo_estado}")
            
            # ⭐ CRÍTICO: Actualizar en la base de datos
            resultado = actualizar_estado_empleado(dni, nuevo_estado)
            if resultado:
                print(f"✅ Estado guardado en BD correctamente")
            else:
                print(f"❌ ERROR: No se pudo guardar el estado en BD")
            
            # Registrar el reconocimiento
            registrar_reconocimiento(dni, confidence)
            
            # Notificar cambio
            notificar_empleado_actualizado(dni, nuevo_estado)
            print('❌No se ha reconocido al usuario')



            






# RECOGNIZE faces: 
    #1. detectar cara con detection.py del frame que llega 
    #2. pasarlo a grayScale 
    #3. detectar usando el modelo entrenado .xml