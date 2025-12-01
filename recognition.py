#con LBPH: https://www.geeksforgeeks.org/computer-vision/face-recognition-with-local-binary-patterns-lbps-and-opencv/?utm_source=chatgpt.com

import cv2
import os
import numpy as np
import queue_class as queue

frames = queue.detected



def recognition_run():
    print("reconociendo")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    while(True):
        #coger el frame de la cola frames 
        #reconocer el frame 






# RECOGNIZE faces: 
    #1. detectar cara con detection.py del frame que llega 
    #2. pasarlo a grayScale 
    #3. detectar usando el modelo entrenado .xml