from flask import Response, Blueprint
import cv2
import numpy as np
from queue import Empty

from core.queues.colas import show_queue 

video_bp = Blueprint("video",__name__)

def crear_frame_placeholder(texto="Cámara no activa", subtexto=None):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (40, 40, 45)  # Gris oscuro azulado
    
    # Icono de cámara (rectángulo simple)
    cv2.rectangle(frame, (270, 180), (370, 240), (80, 80, 90), -1)
    cv2.circle(frame, (320, 210), 20, (100, 100, 110), -1)
    cv2.circle(frame, (320, 210), 15, (60, 60, 70), -1)
    
    # Texto principal
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(texto, font, 0.8, 2)[0]
    text_x = (640 - text_size[0]) // 2
    cv2.putText(frame, texto, (text_x, 300), font, 0.8, (200, 200, 200), 2)
    
    # Subtexto
    if subtexto:
        subtext_size = cv2.getTextSize(subtexto, font, 0.5, 1)[0]
        subtext_x = (640 - subtext_size[0]) // 2
        cv2.putText(frame, subtexto, (subtext_x, 340), font, 0.5, (150, 150, 150), 1)
    
    return frame

def gen_frames():

    # Frame por defecto cuando no hay cámara activa
    frame_placeholder = crear_frame_placeholder(
        "Camara no activa", 
        "Inicia reconocimiento o registra un empleado"
    )
    ultimo_frame = frame_placeholder.copy()
    
    sin_frames_contador = 0
    
    try:  # try exterior para capturar GeneratorExit
        while True:
            try:
                # Intentar obtener frame con timeout de 0.5 segundos
                # Si la cola está vacía, lanza excepción Empty
                frame = show_queue.get(timeout=0.05)
                ultimo_frame = frame
                sin_frames_contador = 0  # Resetear contador
                
            except Empty:
                # No hay frames disponibles - usar placeholder
                sin_frames_contador += 1
                
                # Después de 3 intentos fallidos, mostrar placeholder
                if sin_frames_contador > 3:
                    frame = frame_placeholder
                else:
                    # Mantener último frame válido brevemente
                    frame = ultimo_frame
                
            except Exception as e:
                # Cualquier otro error - usar último frame válido
                print(f"[VIDEO_FEED] ⚠️ Error obteniendo frame: {e}")
                frame = ultimo_frame

            # Codificar frame a JPEG
            try:
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if not ret:
                    print("[VIDEO_FEED] ❌ Error codificando frame")
                    continue

                frame_bytes = buffer.tobytes()
                
                # Formato MJPEG para streaming HTTP
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       

                       
            except Exception as e:
                print(f"[VIDEO_FEED] ❌ Error en yield: {e}")
                continue
                
    except GeneratorExit:  # Captura exterior por si acaso
        print("[VIDEO_FEED] 🛑 Stream cerrado")
    finally:  # Limpieza garantizada
        print("[VIDEO_FEED] 🧹 Recursos liberados")

@video_bp.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

