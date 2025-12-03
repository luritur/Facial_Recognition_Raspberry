import os
import shutil
import cv2
import time



def borrar_contenido_carpeta(ruta):
    # Borra todo el contenido de la carpeta, incluyendo subcarpetas y archivos
    for nombre in os.listdir(ruta):
        path = os.path.join(ruta, nombre)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


def camara_run(frames, duracion,path, camera_index):  #FALTA DECIDIR Y PROGRAMAR CUANTOS FRAMES SE VAN A GUARDAR EN LA COLA
    cap = cv2.VideoCapture(camera_index)  # Abre la cámara (ojo con el 0)
    borrar_contenido_carpeta("/home/pi/Facial_Recognition_Raspberry/imagenes/frames/")

    print(f"run.py: captura iniciada durante {duracion} segundos")
    inicio = time.time()
    frames_put=0
    #frame_guardado = False   # Para guardar solo un frame
    if("frames" in path):#lanzamos hilo de detectar
        print("detectando........")
    if (path.contains("register")):
        ret, frame = cap.read()
        ruta = f"{path}registro{frames_put}.jpg"
        cv2.imwrite(ruta, frame)
        print(f"Usuario registrado en: {ruta}")
        cap.release()
        return 
    while time.time() - inicio < duracion: #x segundos de while (se pasa como parametro)
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer el frame.")
            break
        frames.put(frame)
        frames_put+=1

        ruta = f"{path}frame{frames_put}.jpg"
        cv2.imwrite(ruta, frame)
        print(f"Frame guardado en: {ruta}")

    cap.release()