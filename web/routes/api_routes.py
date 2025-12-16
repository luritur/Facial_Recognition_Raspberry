

from flask import Blueprint, jsonify, request
import time
import threading
from core.control import stop_event

# Importar módulos de tu código existente
from core.main import ejecutar_run
from core.main import ejecutar_registro
from core.main import detener_run
from core.main import run_entrenar_modelo_thread
# from core.gestion.gestion_empleados import get_empleados_registrados
import core.gestion.gestion_empleados as gestion_empleados
from core.bd.bd_functions import obtener_empleados_lista


# Variables globales para gestión de estado
registro_activo = False
registro_thread = None
employees_data = []  # Lista temporal de empleados (luego la sacarías de una BD o archivo)
reconocimiento_activo=False



# Rutas de configuración
#PATH_REGISTER = "/home/pi/Facial_Recognition_Raspberry/imagenes/registro/"
PATH_REGISTER = "C:/3Año/arquitectura/Facial_Recognition_Raspberry/imagenes/registro"


# Crear el blueprint para el API
api_bp = Blueprint('api', __name__, url_prefix='/api')


#Api endpoints

@api_bp.route('/api/initrecognition', methods=['POST'])
def detectar_start():
    global reconocimiento_activo
    id_actual = gestion_empleados.ultimo_id_reconocimiento
    iniciado = ejecutar_run()
    
    if iniciado:
        reconocimiento_activo = True
        return jsonify({
            "status": "ok",
            "message": "Reconocimiento iniciado",
            "current_id": id_actual
        })
    else:
        # No se pudo iniciar (no hay modelo, etc.)
        reconocimiento_activo = False
        return jsonify({
            "status": "error",
            "message": "No se pudo iniciar el reconocimiento. Verifica que el modelo esté entrenado."
        }), 400

@api_bp.route('/api/stoprecognition', methods=['POST'])
def detectar_stop():
    global reconocimiento_activo
    detener_run()
    reconocimiento_activo=False
    return jsonify({
        "status": "ok",
        "message": "Reconocimiento detenido"
    })


@api_bp.route('/api/check_user_exists', methods=['POST'])
def api_check_user_exists():
    """
    Comprueba si ya existe un usuario con el mismo email o dni.
    Recibe: { "email": "...", "dni": "..." }
    """
    data = request.get_json()
    email = data.get('email', '').strip()
    dni = data.get('dni', '').strip()
    from core.bd.bd_functions import Empleado
    from flask import current_app
    with current_app.app_context():
        existe_email = Empleado.query.filter_by(email=email).first() is not None
        existe_dni = Empleado.query.filter_by(dni=dni).first() is not None
    if existe_email:
        return jsonify({'exists': True, 'field': 'email'}), 200
    if existe_dni:
        return jsonify({'exists': True, 'field': 'dni'}), 200
    return jsonify({'exists': False}), 200

@api_bp.route('/api/registrar', methods=['POST'])
def api_registrar():
    """
    Endpoint para registrar un nuevo empleado con captura facial
    Recibe: { "nombre": "...", "dni": "...", "duracion": 3 }
    """
    global registro_activo, registro_thread
    
    try:
        data = request.get_json()
        # Datos del formulario
        nombre = data.get('nombre', '').strip()
        dni = data.get('dni', '').strip()
        email = data.get('email', '').strip()      # Nuevo campo
        jornada_val = data.get('jornada', '')
        if isinstance(jornada_val, int):
            jornada = jornada_val
        else:
            jornada = int(jornada_val.strip()) if jornada_val else 8
        
        # Configuración (si no viene, usa 8 por defecto)
        duracion = data.get('duracion', 8)
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
            print(f"[API] Iniciando registro para: {nombre}. DNI; {dni}")
                
            ejecutar_registro(nombre, dni, email, jornada)

                
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



@api_bp.route('/api/entrenarModelo', methods=['POST'])
def api_entrenarModelo():
    empleados = obtener_empleados_lista()

    # Si NO hay empleados, devolver mensaje y NO entrenar
    if not empleados:   # Esto cubre None o lista vacía
        return jsonify({
            'status': 'error',
            'message': 'No habría empleados para entrenar el modelo'
        }), 400

    # Si sí hay empleados, entrenar
    run_entrenar_modelo_thread()

    return jsonify({
        'status': 'ok',
        'message': 'Modelo entrenado'
    })

@api_bp.route('/api/entrenamiento/progreso', methods=['GET'])
def obtener_progreso_entrenamiento():
    """Devuelve el progreso actual del entrenamiento"""
    import core.control as control
    return jsonify({
        'entrenando': control.entrenando_modelo,
        'progreso': control.entrenamiento_progreso,
        'mensaje': control.entrenamiento_mensaje
    })


############################################################


@api_bp.route('/empleados', methods=['GET'])
def obtener_empleados():
    """Devuelve empleados actuales"""
    empleados = obtener_empleados_lista()
    
    # Convertir objetos Empleado a diccionarios
    empleados_dict = [
        {
            'nombre': emp.nombre,
            'dni': emp.dni,
            'email': emp.email,
            'jornada': emp.jornada,
            'horas': emp.horas_trabajadas if hasattr(emp, 'horas_trabajadas') else 0,
            'estado': emp.estado if hasattr(emp, 'estado') else 'out'
        }
        for emp in empleados
    ]
    
    return jsonify({
        'success': True,
        'empleados': empleados_dict,
        'version': gestion_empleados.empleados_version
    })

@api_bp.route('/empleados/esperar-cambios', methods=['GET'])
def esperar_cambios():
    """Long polling: espera hasta que haya cambios"""
    version_actual = int(request.args.get('version', 0))
    timeout = 30
    inicio = time.time()
    
    print(f"[LONG POLLING] 🔍 Cliente esperando cambios. Versión actual: {version_actual}")
    print(f"[LONG POLLING] 📊 Versión del servidor: {gestion_empleados.empleados_version}")
    
    while (time.time() - inicio) < timeout:
        with gestion_empleados.empleados_lock:
            if gestion_empleados.empleados_version > version_actual:
                print(f"[LONG POLLING] 🎉 ¡Cambio detectado! {gestion_empleados.empleados_version} > {version_actual}")
                print(f"[LONG POLLING] 📦 Enviando: {gestion_empleados.ultimo_cambio}")

                tipo_cambio = gestion_empleados.ultimo_cambio['tipo']
                empleado_data = gestion_empleados.ultimo_cambio['empleado']
                
                # Si es actualización de estado, obtener datos completos de la BD
                if tipo_cambio == 'actualizado':
                    dni = empleado_data['dni']
                    empleados = obtener_empleados_lista()
                    
                    for emp in empleados:
                        if emp.dni == dni:
                            empleado_data = {
                                'dni': emp.dni,
                                'nombre': emp.nombre,
                                'email': emp.email,
                                'jornada': emp.jornada,
                                'horas': emp.horas,
                                'estado': emp.estado  # Estado actualizado de la BD
                            }
                            break
                
                return jsonify({
                    'success': True,
                    'cambio': True,
                    'version': gestion_empleados.empleados_version,
                    'tipo': tipo_cambio,
                    'empleado': empleado_data
                })
        
        time.sleep(0.5)
    
    print(f"[LONG POLLING] ⏰ Timeout. No hubo cambios.")
    return jsonify({
        'success': True,
        'cambio': False,
        'version': version_actual
    })

@api_bp.route('/api/delete_employee', methods=['POST'])
def api_delete_employee():
    """
    Elimina un empleado por DNI.
    Recibe: { "dni": "..." }
    """
    data = request.get_json()
    dni = data.get('dni', '').strip()
    from core.bd.bd_functions import borrar_empleado
    try:
        # Verificar si es el último empleado ANTES de borrarlo
        empleados_antes = obtener_empleados_lista()
        es_ultimo = len(empleados_antes) == 1
        
        borrar_empleado(dni)
        
        respuesta = {
            'status': 'ok', 
            'message': 'Empleado eliminado',
            'es_ultimo': es_ultimo
        }
        
        if es_ultimo:
            respuesta['warning'] = 'Has eliminado al último empleado. El modelo ha sido eliminado. Necesitas registrar al menos un empleado y entrenar el modelo nuevamente.'
        
        return jsonify(respuesta), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    



@api_bp.route('/api/cancelar_registro', methods=['POST'])
def cancelar_registro():
    """
    Cancela el registro de empleado en curso (detiene la grabación si está activa).
    """
    detener_run()    
    return jsonify({'status': 'ok', 'message': 'Registro cancelado'}), 200




@api_bp.route('/recognition_event', methods=['GET'])
def recognition_event():
    """
    Long polling: espera hasta que haya un nuevo reconocimiento
    """
    last_client_id = int(request.args.get('last', 0))
    timeout = 30
    start = time.time()

    print(f"[RECOGNITION POLLING] 👀 Cliente esperando evento. Último cliente ID: {last_client_id}")
    print(f"[RECOGNITION POLLING] 🧠 Último ID del servidor: {gestion_empleados.ultimo_id_reconocimiento}")

    while (time.time() - start) < timeout:
        with gestion_empleados.empleados_lock:  
            if gestion_empleados.ultimo_id_reconocimiento > last_client_id:
                print(f"[RECOGNITION POLLING] 🎉 Nuevo reconocimiento detectado!")
                print(f"[RECOGNITION POLLING] 📢 Mensaje: {gestion_empleados.ultima_persona_reconocida}")

                return jsonify({
                    'success': True,
                    'nuevo': True,
                    'id': gestion_empleados.ultimo_id_reconocimiento,
                    'mensaje': gestion_empleados.ultima_persona_reconocida,
                    'confidence': gestion_empleados.confidence
                })

        time.sleep(0.5)

    # No hubo cambios → mantener conexión viva
    print(f"[RECOGNITION POLLING] ⏰ Timeout sin cambios")

    return jsonify({
        'success': True,
        'nuevo': False,
        'id': last_client_id
    })
