import mediapipe as mp
import queue_class as queue
import cv2
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
frames = queue.frames



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
                    queue.detected.put(frame) #pasamos frame a la cola para reconocer 
                    mp_drawing.draw_detection(frame, detection) #modifica el frame y le pone un rectangulo 
                    queue.show_queue.put(frame)
                    
            else: 
                print("cara no detectada------")
                queue.show_queue.put(frame)






    