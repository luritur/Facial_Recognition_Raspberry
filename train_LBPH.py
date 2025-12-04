    #1.recorrer la carpeta de caras registradas: 
    #   - En una lista guardar el "label" == el nombre del fichero (el nombre del usuario)
    #       -->OJOJO para los labels hay que hacer un diccionario "Nombre":numero
    #   - En otra lista detectar la cara con detection.py + pasarla a gray + guardarla en una lista de imagenes

    #2. entrenar con caras y labels
    #3. guardar el modelo entrenado como un fichero .xml
import cv2
import numpy as np
import detection


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



    

