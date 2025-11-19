from gpiozero import Button, LED
import threading
import queue
import time
import cv2

# botones
BTN_RUN = Button(23, pull_up=True) 
BTN_PAUSE = Button(24, pull_up=True)    # igual no lo usamos

if BTN_RUN.is_pressed():
        run()

def run():
    # inicilizar cola
    frames = queue.Queue()
    #empezar grabacion 
    cap = cv2.VideoCapture(0)  # Abre la cámara (ojo con el 0)
    #ir metiendo los frames a la cola 
    inicio = time.time()          # Momento en que empieza
    duracion = 10  
    while time.time() - inicio < duracion:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer el frame.")
            break
        frames.put(frame)
        cv2.imshow("Cámara", frame)  # Muestra el frame en una ventana llamada "Cámara" (camara/ventana)
    # Espera 1 ms y revisa si se presionó la tecla ESC (código 27)
        
    for frame in frames:
         if frame in csvFrames:
              print("detectado")
              break


#
#cap = cv2.VideoCapture(0)  # Abre la cámara

#while True:
#    ret, frame = cap.read()
#    if not ret:
#        print("No se pudo leer el frame.")
#        break

#   cv2.imshow("Cámara", frame)  # Muestra el frame en una ventana llamada "Cámara" (camara/ventana)

    # Espera 1 ms y revisa si se presionó la tecla ESC (código 27)
#    if cv2.waitKey(x) & 0xFF == 27:    x=tiempo de cada frame (1000/60)
#        break

#cap.release()
#cv2.destroyAllWindows()
#if cv2.waitKey(x) & 0xFF == 27:    #x=tiempo de cada frame (1000/60)
            #break