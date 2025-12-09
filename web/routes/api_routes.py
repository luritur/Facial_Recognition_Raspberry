from flask import Blueprint, jsonify, request



# Importar módulos de tu código existente
from core.main import ejecutar_run
from core.main import ejecutar_registro
from core.main import detener_run

# Variables globales para gestión de estado
registro_activo = False
registro_thread = None
employees_data = []  # Lista temporal de empleados (luego la sacarías de una BD o archivo)

# Rutas de configuración
#PATH_REGISTER = "/home/pi/Facial_Recognition_Raspberry/imagenes/registro/"
PATH_REGISTER = "C:/3Año/arquitectura/Facial_Recognition_Raspberry/imagenes/registro"


# Crear el blueprint para el API
api_bp = Blueprint('api', __name__, url_prefix='/api')


#Api endpoints

@api_bp.route('/api/initrecognition', methods=['POST'])
def detectar_start():
    ejecutar_run()
    return jsonify({
        "status": "ok",
        "message": "Reconocimiento iniciado"
    })

@api_bp.route('/api/stoprecognition', methods=['POST'])
def detectar_stop():
    detener_run()
    return jsonify({
        "status": "ok",
        "message": "Reconocimiento detenido"
    })

@api_bp.route('/agregar_empleado', methods=['POST'])
def agregar_empleado():
    """Endpoint legacy - redirige al nuevo sistema"""
    return jsonify({
        "status": "redirect",
        "message": "Usa el nuevo modal paso a paso"
    })

@api_bp.route('/api/registrar', methods=['POST'])
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
        
        try:
            print(f"[API] Iniciando registro para: {nombre}")
                
            ejecutar_registro(nombre)
                
            print(f"[API] Registro completado para: {nombre}")
                
        except Exception as e:
            print(f"[API] Error en registro: {e}")
        finally:
            registro_activo = False
        
        
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

@api_bp.route('/api/registrar/stop', methods=['POST'])
def api_registrar_stop():
    """Detiene el proceso de registro (si es necesario)"""
    global registro_activo
    
    registro_activo = False
    
    return jsonify({
        'status': 'ok',
        'message': 'Registro detenido'
    })