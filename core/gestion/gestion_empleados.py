import threading
from core.bd.bd_functions import obtener_empleados_lista
from core.bd.bd_functions import get_empleado_name
# Variables globales para notificar cambios
empleados_version = 0
empleados_lock = threading.Lock()
ultimo_cambio = None

#para reconcimiento:
ultimo_id_reconocimiento= 0
ultima_persona_reconocida = None
confidence = 0.0


def notificar_nuevo_empleado(dni, nombre, email, jornada, horas=0, estado='out'):
    """Llama esto cuando REGISTRES un empleado nuevo"""
    global empleados_version, ultimo_cambio
    
    print(f"[NOTIFICACION] 🔔 Iniciando notificación para: {nombre}")
    
    # # PRIMERO: Agregar a la lista
    # agregar_empleado_a_lista(nombre, email, jornada, horas, estado)
    
    # SEGUNDO: Notificar el cambio
    with empleados_lock:
        version_anterior = empleados_version
        empleados_version += 1
        ultimo_cambio = {
            'tipo': 'nuevo',
            'empleado': {
                'nombre': nombre,
                'dni': dni,
                'email': email,
                'jornada': jornada,
                'horas': horas,
                'estado': estado
            }
        }
        print(f"[NOTIFICACION] 📊 Versión: {version_anterior} → {empleados_version}")
        print(f"[NOTIFICACION] 📦 Ultimo cambio: {ultimo_cambio}")
    
    print(f"[NOTIFICACION] ✅ Notificación completada para: {nombre}")

def notificar_empleado_actualizado(dni, estado):
    global empleados_version, ultimo_cambio
    
    with empleados_lock:
        # Actualizar en la lista
        empleados = obtener_empleados_lista()
        for emp in empleados:
            if emp.dni == dni:  # Cambio aquí: emp.dni en lugar de emp['dni']
                # No puedes modificar emp.estado directamente aquí porque es un objeto de BD
                print(f"[GESTION] 🔄 Empleado {dni} actualizado. del estado a: {estado}")
                break
        
        # Notificar el cambio
        empleados_version += 1
        ultimo_cambio = {
            'tipo': 'actualizado',
            'empleado': {
                'dni': dni,
                'estado': estado
            }
        }
        print(f"[NOTIFICACION] 🔔 Notificado actualización: {dni} - estado cambiado a {estado}")

    


def registrar_reconocimiento(dni, confidence_param):
    global ultimo_id_reconocimiento, ultima_persona_reconocida, confidence

    confidence = round(confidence_param,2)
    ultimo_id_reconocimiento += 1
    ultima_persona_reconocida = get_empleado_name(dni)
    ultima_persona_reconocida = f"Se ha reconocido a {ultima_persona_reconocida}"
