import mediapipe as mp
import core.queues.colas as queue
import cv2
import os
from core.control import stop_event
from queue import Full, Empty

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
frames = queue.frames

#OJOJO VER REALMENTE CUALES SON LAS DIMENSIONES
IMAGE_WIDTH = 720
IMAGE_HEIGHT = 360


def detection_run():
    print("detectando en detection_run....")
    with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
        while not stop_event.is_set():
            try:
                frame = frames.get(timeout=0.1)  # Intenta obtener el frame con un timeout
                if frame is None:
                    continue

                # Procesamiento de la imagen
                frame.flags.writeable = False
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_detection.process(frame_rgb)

                frame.flags.writeable = True
                if results.detections:
                    print("CARA DETECTADA !!!!!!!")
                    h_img, w_img = frame.shape[:2]
                    for detection in results.detections:
                        bbox = detection.location_data.relative_bounding_box
                        x = int(bbox.xmin * w_img)
                        y = int(bbox.ymin * h_img)
                        w = int(bbox.width * w_img)
                        h = int(bbox.height * h_img)

                        # Clampear valores para que estén dentro de los límites
                        x = max(0, x)
                        y = max(0, y)
                        w = max(0, min(w, w_img - x))
                        h = max(0, min(h, h_img - y))

                        if w == 0 or h == 0:
                            print("Bounding box inválido, saltando.")
                            continue

                        face_crop = frame[y:y+h, x:x+w]  # frame es BGR
                        if face_crop.size == 0:
                            print("face_crop vacío, saltando.")
                            continue

                        face_gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)  # Convertir a escala de grises
                        face_gray = cv2.resize(face_gray, (100, 100))
                        queue.detected.put(face_gray)
                        mp_drawing.draw_detection(frame, detection)

                else:
                    print("cara no detectada------")

                # Intenta poner el frame en la cola de visualización
                try:
                    queue.show_queue.put(frame, timeout=0.1)
                except Full:
                    pass  # Descartar el frame si la cola está llena

            except Empty:
                # Si la cola está vacía, simplemente saltamos este ciclo sin detener el thread
                print("[Detecting] Cola vacía, esperando por un nuevo frame...")
                continue  # Reinicia el ciclo sin bloqueos



### para entrenar el LBPH
def namesToDictionary(path):
    names_labels = {}
    contador = 1

    print("𝙻𝚘𝚊𝚍𝚒𝚗𝚐: nombres de empleados como labels para el modelo")
    for item in os.listdir(path):
        full_path = os.path.join(path, item)

        # Verificar si es una carpeta
        if os.path.isdir(full_path):
            print("carpeta:" + item)

            name = item  # El nombre de la carpeta ES el dni de la persona
            print("name:" + name)

            names_labels[name] = contador
            print(f"label:{contador}")

            contador += 1

    return names_labels


def frame_detection(path, names_labels):  # usado para el train
    faces = []
    labels = []

    with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            person_name = item
            if os.path.isdir(full_path):
                for file in os.listdir(full_path):
                    if file.endswith('.jpg'):
                        img_path = os.path.join(full_path, file)
                        image_bgr = cv2.imread(img_path)
                        if image_bgr is None:
                            print(f"No se pudo leer la imagen: {img_path}")
                            continue

                        # Para mediapipe necesitamos RGB
                        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
                        image_rgb.flags.writeable = False
                        results = face_detection.process(image_rgb)

                        if results.detections:
                            print("train detection: cara detectada")
                            h_img, w_img = image_rgb.shape[:2]
                            for detection in results.detections:
                                bbox = detection.location_data.relative_bounding_box
                                x = int(bbox.xmin * w_img)
                                y = int(bbox.ymin * h_img)
                                w = int(bbox.width * w_img)
                                h = int(bbox.height * h_img)

                                # Clamp
                                x = max(0, x)
                                y = max(0, y)
                                w = max(0, min(w, w_img - x))
                                h = max(0, min(h, h_img - y))

                                if w == 0 or h == 0:
                                    print("Bounding box invÃ¡lido en train, saltando.")
                                    continue

                                face_crop_rgb = image_rgb[y:y+h, x:x+w]
                                if face_crop_rgb.size == 0:
                                    print("face_crop vacÃ­o en train, saltando.")
                                    continue

                                # image_rgb -> gray: usar RGB2GRAY
                                face_gray = cv2.cvtColor(face_crop_rgb, cv2.COLOR_RGB2GRAY)
                                face_gray = cv2.resize(face_gray, (100, 100))
                                faces.append(face_gray)
                                labels.append(names_labels[person_name])
                        else:
                            print("train detection: caras NO detectada")

    return faces, labels


def boolean_face_detection(image): 
    res = False
    with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
        if image is None:
            return False
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_detection.process(image)
           
        if results.detections: #en results se guarda una lista de caras detectadas
            res = True
        else: 
            print("train detection: caras NO detectada")
    return res