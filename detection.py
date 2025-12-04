import mediapipe as mp
import queue_class as queue
import cv2
import os
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
frames = queue.frames

#OJOJO VER REALMENTE CUALES SON LAS DIMENSIONES
IMAGE_WIDTH = 720
IMAGE_HEIGHT = 360


def detection_run():
    print("detectando en detection_run....")
    with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection: #'with' para liberar recursos automaticamente
        while(True): 
            frame = frames.get()

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            frame.flags.writeable = False
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(frame)

            # Draw the face detection annotations on the image.
            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            if results.detections: #en results se guarda una lista de caras detectadas
                print("CARA DETECTADA !!!!!!!")
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    x, y, w, h = int(bbox.xmin * IMAGE_WIDTH), int(bbox.ymin * IMAGE_HEIGHT), int(bbox.width * IMAGE_WIDTH), int(bbox.height * IMAGE_HEIGHT)
                    face_crop = frame[y:y+h, x:x+w]
                    face_gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY) #lbph trabaja con imagenes en escala de grises
                    queue.detected.put(face_gray) #pasamos frame a la cola para reconocer 
                    mp_drawing.draw_detection(frame, detection) #modifica el frame y le pone un rectangulo 
                    queue.show_queue.put(frame)
                    
            else: 
                print("cara no detectada------")
                queue.show_queue.put(frame)



### para entrenar el LBPH
def namesToDictionary(path):
    names_labels = {}
    contador = 1

    for item in os.listdir(path):
        full_path = os.path.join(path, item)

        # Verificar si es una carpeta
        if os.path.isdir(full_path):
            print("carpeta:" + item)

            name = item  # El nombre de la carpeta ES el nombre de la persona
            print("name:" + name)

            names_labels[name] = contador
            print(f"label:{contador}")

            contador += 1

    return names_labels


def frame_detection(path, names_labels): #usado para el train
    faces = []
    labels = []

    with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection: #'with' para liberar recursos automaticamente
        for item in os.listdir(path): #recorremos las carpetas de las fotos de cada persona
            full_path = os.path.join(path, item)
            person_name = item
            if os.path.isdir(full_path):
                lista_frames_persona = []

                for file in os.listdir(full_path):
                    if file.endswith('.jpg'):
                        image = cv2.imread(os.path.join(full_path, file)) # OJOOJOJ

                        image.flags.writeable = False
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        results = face_detection.process(image)

                        if results.detections: #en results se guarda una lista de caras detectadas
                            print("train detection: cara detectada")
                            for detection in results.detections: #obtenemos la region de la cara ya que lbph trabaja con eso
                                bbox = detection.location_data.relative_bounding_box
                                x, y, w, h = int(bbox.xmin * IMAGE_WIDTH), int(bbox.ymin * IMAGE_HEIGHT), int(bbox.width * IMAGE_WIDTH), int(bbox.height * IMAGE_HEIGHT)
                                face_crop = image[y:y+h, x:x+w]
                                face_gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY) #lbph trabaja con imagenes en escala de grises

                                lista_frames_persona.append(face_gray)
                
                        else: 
                            print("train detection: caras NO detectada")
                labels.append(names_labels[person_name])
                faces.append(lista_frames_persona)

    return faces, labels

def boolean_face_detection(image): 
    res = False
    with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_detection.process(image)
           
        if results.detections: #en results se guarda una lista de caras detectadas
            res = True
        else: 
            print("train detection: caras NO detectada")
    return res




    