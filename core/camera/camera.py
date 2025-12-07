import os
import shutil
import cv2
import time
import core.detection.detection as detection



def borrar_contenido_carpeta(ruta):
    # Borra todo el contenido de la carpeta, incluyendo subcarpetas y archivos
    for nombre in os.listdir(ruta):
        path = os.path.join(ruta, nombre)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
            

def _open_camera_with_retries(camera_index, retries=3, delay=1.0):
    """Intentar abrir la camara varias veces."""
    for intento in range(1, retries+1):
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            return cap
        else:
            try:
                cap.release()
            except Exception:
                pass
            time.sleep(delay)
    return None


def camara_run(frames, duracion,path, camera_index, nombre_persona=None):  #FALTA DECIDIR Y PROGRAMAR CUANTOS FRAMES SE VAN A GUARDAR EN LA COLA
    cap = _open_camera_with_retries(camera_index, retries=4, delay=0.8)
    if cap is None:
        print(f"ERROR: No se pudo abrir la camara index={camera_index} tras varios intentos")
        return
    
    try:
        if "frames" in path:
            borrar_contenido_carpeta(path)
        os.makedirs(path, exist_ok=True)

        print(f"run.py: captura iniciada durante {duracion} segundos")
        inicio = time.time()
        frames_put=1
        consecutive_failures = 0
        MAX_CONSECUTIVE_FAILURES = 6
        if nombre_persona is not None:
            # Crear carpeta de la persona
            carpeta_persona = os.path.join(path, nombre_persona)
            os.makedirs(carpeta_persona, exist_ok=True)
            minimo_una_cara_detectada = None

            while time.time() - inicio < duracion:
                ret, frame = cap.read()
                if not ret or frame is None:
                    consecutive_failures += 1
                    print(f"Fallo al leer el frame. Intento {consecutive_failures}/{MAX_CONSECUTIVE_FAILURES}")
                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        print("Demasiados fallos consecutivos al leer frames. Abortando captura.")
                        cap.release()
                        time.sleep(0.8)
                        cap = _open_camera_with_retries(camera_index, retries=3, delay=0.8)
                        if cap is None:
                            print("[camera] No se pudo reabrir la camara, saliendo del bucle de registro.")
                            break
                        consecutive_failures = 0
                    continue

                consecutive_failures = 0
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
            os.makedirs(path, exist_ok=True)
            while time.time() - inicio < duracion: #x segundos de while (se pasa como parametro)
                ret, frame = cap.read()
                if not ret or frame is None:
                    consecutive_failures += 1
                    print(f"[camera] read failed ({consecutive_failures}). ret={ret}")
                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        print("[camera] Reiniciando camera por fallos consecutivos...")
                        cap.release()
                        time.sleep(0.8)
                        cap = _open_camera_with_retries(camera_index, retries=3, delay=0.8)
                        if cap is None:
                            print("[camera] No se pudo reabrir la camara, saliendo del bucle de run.")
                            break
                        consecutive_failures = 0
                    continue

                consecutive_failures = 0

                try:
                    frames.put(frame)
                except Exception as e:
                    # No dejar que la encolada detenga el hilo; solo loggear
                    print(f"[camera] Error al encolar frame: {e}")

                # Guardar copia en disco (nombres Ãºnicos)
                ruta = os.path.join(path, f"frame{frames_put}.jpg")
                cv2.imwrite(ruta, frame)
                print(f"Frame guardado en: {ruta}")
                frames_put += 1
    finally:
        try:
            cap.release()
            print("[camera] camara liberada correctamente.")
        except Exception as e:
            print(f"[camera] Error liberando camara: {e}")
    
    return