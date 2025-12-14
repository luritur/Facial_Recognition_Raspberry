

from flask import Blueprint, jsonify, request
import time
import threading
from core.control import stop_event
import os

# Importar módulos de tu código existente
from core.main import ejecutar_run
from core.main import ejecutar_registro
from core.main import detener_run
from core.main import run_entrenar_modelo_thread
# from core.gestion.gestion_empleados import get_empleados_registrados
import core.gestion.gestion_empleados as gestion_empleados
from core.bd.bd_functions import obtener_empleados_lista
import config


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
    if config.recognizer is None or config.names_labels is None:
        return jsonify({
            "status": "error",
            "message": "No hay modelo entrenado. Registra empleados y entrena el modelo primero.",
            "notification": {
                "type": "error",
                "title": "Modelo no disponible",
                "message": "Debes entrenar el modelo antes de iniciar el reconocimiento"
            }
        }), 400
    empleados = obtener_empleados_lista()
    if not empleados:
        return jsonify({
            "status": "error",
            "message": "No hay empleados registrados",
            "notification": {
                "type": "error",
                "title": "Sin empleados",
                "message": "Registra al menos un empleado antes de iniciar el reconocimiento"
            }
        }), 400
    
    ejecutar_run()

    return jsonify({
        "status": "ok",
        "message": "Reconocimiento iniciado",
        "notification": {
            "type": "success",
            "title": "Reconocimiento iniciado",
            "message": f"Sistema activo. {len(empleados)} empleado(s) en la base de datos"
        }
    })

@api_bp.route('/api/stoprecognition', methods=['POST'])
def detectar_stop():
    detener_run()
    return jsonify({
        "status": "ok",
        "message": "Reconocimiento detenido",
        "notification": {
            "type": "info",
            "title": "Reconocimiento detenido",
            "message": "El sistema de reconocimiento facial ha sido detenido"
        }
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
            'message': 'No habría empleados para entrenar el modelo',
            'notification': {
                'type': 'error',
                'title': 'Sin empleados',
                'message': 'Registra al menos un empleado antes de entrenar el modelo'
            }
        }), 400

    # Si sí hay empleados, entrenar
    run_entrenar_modelo_thread()

    return jsonify({
        'status': 'ok',
        'message': 'Modelo entrenado',
        'notification': {
            'type': 'success',
            'title': 'Entrenamiento iniciado',
            'message': f'Entrenando modelo con {len(empleados)} empleado(s). Esto puede tomar unos segundos...'
        }
    })

@api_bp.route('/api/modelo_status', methods=['GET'])
def api_modelo_status():
    """Obtiene el estado del modelo y el entrenamiento"""
    import core.control as control
    
    tiene_modelo = config.recognizer is not None and config.names_labels is not None
    entrenando = control.entrenando_modelo
    num_empleados = len(obtener_empleados_lista())
    
    return jsonify({
        'tiene_modelo': tiene_modelo,
        'entrenando': entrenando,
        'num_empleados': num_empleados,
        'empleados_registrados': config.names_labels if config.names_labels else {}
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
    """Long polling UNIFICADO: espera cambios de cualquier tipo"""
    version_actual = int(request.args.get('version', 0))
    timeout = 30
    inicio = time.time()
    
    print(f"[LONG POLLING] 🔍 Cliente esperando cambios. Versión cliente: {version_actual}")
    print(f"[LONG POLLING] 📊 Versión servidor: {gestion_empleados.empleados_version}")
    
    with gestion_empleados.empleados_condition:
        # Si ya hay cambios disponibles, responder inmediatamente
        if gestion_empleados.empleados_version > version_actual:
            print(f"[LONG POLLING] ⚡ Cambio ya disponible!")
            if gestion_empleados.ultimo_cambio:
                print(f"[LONG POLLING] 📦 Tipo: {gestion_empleados.ultimo_cambio['tipo']}")
            
            return jsonify({
                'success': True,
                'cambio': True,
                'version': gestion_empleados.empleados_version,
                'tipo': gestion_empleados.ultimo_cambio['tipo'] if gestion_empleados.ultimo_cambio else 'desconocido',
                'empleado': gestion_empleados.ultimo_cambio['empleado'] if gestion_empleados.ultimo_cambio else {}
            })
        
        # No hay cambios aún, esperar con timeout
        tiempo_restante = timeout
        while tiempo_restante > 0:
            # wait() libera el lock y espera señal o timeout
            señal_recibida = gestion_empleados.empleados_condition.wait(timeout=tiempo_restante)
            
            # Si se recibió señal y hay cambios
            if gestion_empleados.empleados_version > version_actual:
                print(f"[LONG POLLING] 🎉 ¡Cambio detectado por señal!")
                if gestion_empleados.ultimo_cambio:
                    print(f"[LONG POLLING] 📦 Tipo: {gestion_empleados.ultimo_cambio['tipo']}")
                
                return jsonify({
                    'success': True,
                    'cambio': True,
                    'version': gestion_empleados.empleados_version,
                    'tipo': gestion_empleados.ultimo_cambio['tipo'] if gestion_empleados.ultimo_cambio else 'desconocido',
                    'empleado': gestion_empleados.ultimo_cambio['empleado'] if gestion_empleados.ultimo_cambio else {}
                })
            
            # Actualizar tiempo restante
            tiempo_restante = timeout - (time.time() - inicio)
    
    # Timeout sin cambios
    print(f"[LONG POLLING] ⏰ Timeout (30s). Sin cambios.")
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
        # Verificar cuántos empleados quedan
        empleados = obtener_empleados_lista()
        es_ultimo = len(empleados) == 1
        
        borrar_empleado(dni)
        
        # Si era el último empleado, enviar notificación especial
        if es_ultimo:
            return jsonify({
                'status': 'ok',
                'message': 'Último empleado eliminado',
                'notification': {
                    'type': 'warning',
                    'title': 'Último empleado eliminado',
                    'message': 'El modelo ha sido eliminado. Deberás entrenar el modelo nuevamente cuando registres nuevos empleados.'
                }
            }), 200
        
        return jsonify({
            'status': 'ok',
            'message': 'Empleado eliminado',
            'notification': {
                'type': 'success',
                'title': 'Empleado eliminado',
                'message': 'El empleado ha sido eliminado correctamente. Recuerda entrenar el modelo nuevamente.'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'notification': {
                'type': 'error',
                'title': 'Error al eliminar',
                'message': f'No se pudo eliminar el empleado: {str(e)}'
            }
        }), 500

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
        with gestion_empleados.empleados_condition:  
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

'''
@api_bp.route('/api/empleados_estado_actualizar', methods=['GET'])
def empleados_estado_actualizar():
    """
    Endpoint específico para detectar cambios de estado.
    Devuelve la versión actual y el último cambio de estado.
    """
    return jsonify({
        'version': gestion_empleados.empleados_version,
        'ultimo_cambio': gestion_empleados.ultimo_cambio
    })
'''