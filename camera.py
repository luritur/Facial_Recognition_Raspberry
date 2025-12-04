import os
import shutil
import cv2
import time
import detection



def borrar_contenido_carpeta(ruta):
    # Borra todo el contenido de la carpeta, incluyendo subcarpetas y archivos
    for nombre in os.listdir(ruta):
        path = os.path.join(ruta, nombre)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


def camara_run(frames, duracion,path, camera_index, nombre_persona=None):  #FALTA DECIDIR Y PROGRAMAR CUANTOS FRAMES SE VAN A GUARDAR EN LA COLA
    cap = cv2.VideoCapture(camera_index)  # Abre la cámara (ojo con el 0)
    borrar_contenido_carpeta("/home/pi/Facial_Recognition_Raspberry/imagenes/frames/")

    print(f"run.py: captura iniciada durante {duracion} segundos")
    inicio = time.time()
    frames_put=1
    if("frames" in path):#lanzamos hilo de detectar
        print("detectando........")
    if nombre_persona is not None:
        # Crear carpeta de la persona
        carpeta_persona = os.path.join(path, nombre_persona)
        os.makedirs(carpeta_persona, exist_ok=True)
        minimo_una_cara_detectada = None
        while time.time() - inicio < duracion:
            ret, frame = cap.read()
            if not ret:
                print("No se pudo leer el frame.")
                break
            if detection.boolean_face_detection(frame): #guardamos solo las fotos que tienen cara
                ruta = os.path.join(carpeta_persona, f"{frames_put}.jpg")
                cv2.imwrite(ruta, frame)
                print(f"Foto registrada en: {ruta}")
                frames_put += 1
                minimo_una_cara_detectada = True

        if(minimo_una_cara_detectada):
            print(f"Registro completado para {nombre_persona}")
        else: 
            print(f"No se ha detectado ninguna cara {nombre_persona}")

    else: 
        while time.time() - inicio < duracion: #x segundos de while (se pasa como parametro)
            ret, frame = cap.read()
            if not ret:
                print("No se pudo leer el frame.")
                break
            frames.put(frame)

            ruta = f"{path}frame{frames_put}.jpg"
            cv2.imwrite(ruta, frame)
            print(f"Frame guardado en: {ruta}")
            frames_put+=1
    cap.release()
    