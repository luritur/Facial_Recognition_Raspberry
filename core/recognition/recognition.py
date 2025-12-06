#con LBPH: https://www.geeksforgeeks.org/computer-vision/face-recognition-with-local-binary-patterns-lbps-and-opencv/?utm_source=chatgpt.com

import cv2
import os
import numpy as np
import core.queues.queue_class as queue
import core.detection.detection as detection 

frames = queue.detected


def recognition_run(recognizer, names_labels): #OJOJO como hacer para cerrar el bucle
    label_name = {value: key for key, value in names_labels.items()} #invertir el diccionario
    print("reconociendo")
    while(True):
        #coger el frame de la cola frames 
        #reconocer el frame 
        frame = frames.get()

        # Recognize and label the faces
            # Recognize the face using the trained model
        label, confidence = recognizer.predict(frame)
            #print(confidence)
        if confidence > 50:
            # Display the recognized label and confidence level
            #cv2.putText(frame, label_name[label], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
            # Draw a rectangle around the face
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            print(f"Se ha reconocido al usuario: {label_name[label]}")
        else:
            print('No se ha reconocido al usuario')

        # Display the frame with face recognition
        cv2.imshow('Recognize Faces', frame)







# RECOGNIZE faces: 
    #1. detectar cara con detection.py del frame que llega 
    #2. pasarlo a grayScale 
    #3. detectar usando el modelo entrenado .xml