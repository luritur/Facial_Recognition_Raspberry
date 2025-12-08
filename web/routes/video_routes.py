from flask import Response, Blueprint
import cv2

from core.queues.queue_class import show_queue 

video_bp = Blueprint("video",__name__)



def gen_frames():
    """Generador de frames para el stream MJPEG"""
    while True:
        frame = show_queue.get()
        if frame is None:
            continue

        # Codificar frame a JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        # Formato MJPEG para streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@video_bp.route('/recognition_video_feed')
def recognition_video_feed():
    """Endpoint que devuelve el stream de video"""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@video_bp.route('/register_video_feed')
def register_video_feed():
    """
    Stream de video en tiempo real
    TODO: Implementar con un gestor de cámara que corra continuamente
    """
    def generate():
        # Placeholder - esto deberías implementarlo con un CameraManager
        # que tenga la cámara siempre abierta
        
        cap = cv2.VideoCapture(0)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Codificar frame a JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        finally:
            cap.release()
    
    return Response(generate(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')