from flask import Flask, render_template, Response, jsonify, request
import sys
import os
import threading
import cv2

# Añadir el path del proyecto para importar módulos de core/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Importar módulos de tu código existente
import core.camera.camera as camera
import core.queues.queue_class as queue
import core.detection.detection as detection
import core.recognition.train_LBPH as train

app = Flask(__name__)

# Variables globales para gestión de estado
registro_activo = False
registro_thread = None
employees_data = []  # Lista temporal de empleados (luego la sacarías de una BD o archivo)

# Rutas de configuración
PATH_REGISTER = "/home/pi/Facial_Recognition_Raspberry/imagenes/registro/"

# ============================================================
# RUTAS DE PÁGINAS HTML
# ============================================================

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/camara_directo')
def camara_directo():
    return render_template('camara_directo.html')

@app.route('/registro_empleados')
def registro_empleados():
    # Cargar empleados registrados desde la carpeta de registro
    empleados = []
    
    if os.path.exists(PATH_REGISTER):
        for carpeta in os.listdir(PATH_REGISTER):
            carpeta_path = os.path.join(PATH_REGISTER, carpeta)
            if os.path.isdir(carpeta_path):
                # Asumir que el nombre de la carpeta es el nombre del empleado
                # Puedes mejorar esto leyendo de un archivo JSON o BD
                empleados.append({
                    'name': carpeta,
                    'dni': 'N/A',  # Aquí deberías guardar el DNI en algún lado
                })
    
    return render_template('registro_empleados.html', employees=empleados)

@app.route('/base')
def navegar():
    return render_template('base.html')

# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/registrar', methods=['POST'])
def api_registrar():
    """
    Endpoint para registrar un nuevo empleado con captura facial
    Recibe: { "nombre": "...", "dni": "...", "duracion": 3 }
    """
    global registro_activo, registro_thread
    
    try:
        data = request.get_json()
        nombre = data.get('nombre', '').strip()
        dni = data.get('dni', '').strip()
        duracion = data.get('duracion', 3)
        
        if not nombre or not dni:
            return jsonify({
                'status': 'error',
                'message': 'Nombre y DNI son obligatorios'
            }), 400
        
        if registro_activo:
            return jsonify({
                'status': 'error',
                'message': 'Ya hay un registro en proceso'
            }), 409
        
        # Marcar como activo
        registro_activo = True
        
        # Lanzar hilo de captura
        def realizar_registro():
            global registro_activo
            try:
                print(f"[API] Iniciando registro para: {nombre}")
                
                # Aquí llamamos a tu función existente de captura
                # Asumiendo que tienes un índice de cámara configurado
                camIndex = 0
                
                camera.camara_run(
                    frames=queue.Queue(), 
                    duracion=duracion,
                    path=PATH_REGISTER,
                    camera_index=camIndex,
                    nombre_persona=nombre
                )
                
                # Entrenar el modelo después del registro
                print(f"[API] Entrenando modelo con nuevo usuario: {nombre}")
                train.trainLBPH(PATH_REGISTER)
                
                print(f"[API] Registro completado para: {nombre}")
                
            except Exception as e:
                print(f"[API] Error en registro: {e}")
            finally:
                registro_activo = False
        
        registro_thread = threading.Thread(target=realizar_registro, daemon=True)
        registro_thread.start()
        
        return jsonify({
            'status': 'ok',
            'message': f'Registro iniciado para {nombre}. Capturando durante {duracion} segundos...'
        })
        
    except Exception as e:
        registro_activo = False
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/registrar/stop', methods=['POST'])
def api_registrar_stop():
    """Detiene el proceso de registro (si es necesario)"""
    global registro_activo
    
    registro_activo = False
    
    return jsonify({
        'status': 'ok',
        'message': 'Registro detenido'
    })

@app.route('/video_feed')
def video_feed():
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

@app.route('/api/detectar/start', methods=['POST'])
def detectar_start():
    """Inicia detección de rostros (para implementar)"""
    return jsonify({
        "status": "ok",
        "message": "Detección iniciada (pendiente implementación completa)"
    })

@app.route('/api/detectar/stop', methods=['POST'])
def detectar_stop():
    """Detiene detección de rostros (para implementar)"""
    return jsonify({
        "status": "ok",
        "message": "Detección detenida"
    })

@app.route('/agregar_empleado', methods=['POST'])
def agregar_empleado():
    """Endpoint legacy - redirige al nuevo sistema"""
    return jsonify({
        "status": "redirect",
        "message": "Usa el nuevo modal paso a paso"
    })

# ============================================================
# INICIAR APLICACIÓN
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Iniciando Servidor Flask - Sistema de Reconocimiento Facial")
    print("=" * 60)
    print(f"📍 Acceso local: http://localhost:8000")
    print(f"📍 Acceso red:   http://[IP_RASPBERRY]:8000")
    print("=" * 60)
    
    # Crear carpetas necesarias si no existen
    os.makedirs(PATH_REGISTER, exist_ok=True)
    
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)