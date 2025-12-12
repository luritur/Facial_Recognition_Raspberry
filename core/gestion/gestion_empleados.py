import threading
from core.bd.bd_functions import obtener_empleados_lista
# Variables globales para notificar cambios
empleados_version = 0
empleados_lock = threading.Lock()
ultimo_cambio = None



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


def notificar_empleado_actualizado(email, horas, estado):
    """Llama esto cuando ACTUALICES las horas/estado de un empleado"""
    global empleados_version, ultimo_cambio
    
    with empleados_lock:
        # Actualizar en la lista
        empleados = obtener_empleados_lista()
        for emp in empleados:
            if emp['email'] == email:
                emp['horas'] = horas
                emp['estado'] = estado
                print(f"[GESTION] 🔄 Empleado {email} actualizado: {horas}h, {estado}")
                break
        
        # Notificar el cambio
        empleados_version += 1
        ultimo_cambio = {
            'tipo': 'actualizado',
            'empleado': {
                'email': email,
                'horas': horas,
                'estado': estado
            }
        }
        print(f"[NOTIFICACION] 🔔 Notificado actualización: {email} - {horas}h - {estado}")