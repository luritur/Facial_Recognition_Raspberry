import cv2
import numpy as np
import core.detection.detection as detection


def trainLBPH(path):
    faces = []
    labels = []

    names_labels = detection.namesToDictionary(path)
    faces, labels = detection.frame_detection(path, names_labels)

    if len(faces) == 0:
        print("No hay caras detectadas para entrenar. Abortando entrenamiento.")
        return None 

    # Train the face recognition model using the faces and labels
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))



    # Save the trained model to a file
    recognizer.save('/home/pi/Facial_Recognition_Raspberry/trained_model.xml')
    return '/home/pi/Facial_Recognition_Raspberry/trained_model.xml'



    

