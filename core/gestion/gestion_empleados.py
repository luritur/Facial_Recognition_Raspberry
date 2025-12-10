#una funcion que devuelva todos los empleados con sus datos cargados de la BD (se va a usar en api_routes)
import threading


#para probar: 
empleados_prueba = [
    {
        'nombre': 'Pepito Grillo',
        'email': 'pepito.grillo@example.com',
        'jornada': 8,
        'horas': 0,
        'estado': 'no_entro'
    },
    {
        'nombre': 'Marcelo Fernández',
        'email': 'marcelo.fernandez@example.com',
        'jornada': 8,
        'horas': 4,
        'estado': 'trabajando'
    },
    {
        'nombre': 'Ana Torres',
        'email': 'ana.torres@example.com',
        'jornada': 6,
        'horas': 6,
        'estado': 'completado'
    },
    {
        'nombre': 'Luis Martínez',
        'email': 'luis.martinez@example.com',
        'jornada': 8,
        'horas': 2,
        'estado': 'trabajando'
    },
    {
        'nombre': 'Carla Gómez',
        'email': 'carla.gomez@example.com',
        'jornada': 7,
        'horas': 0,
        'estado': 'no_entro'
    }
]

def get_empleados_registrados():
    return empleados_prueba


# Variables globales para notificar cambios
empleados_version = 0
empleados_lock = threading.Lock()
ultimo_cambio = None  # Guardamos el último cambio aquí

def notificar_nuevo_empleado(nombre, email, jornada, horas=0, estado='no_entro'):
    """Llama esto cuando REGISTRES un empleado nuevo"""
    global empleados_version, ultimo_cambio
    
    print(f"[NOTIFICACION] 🔔 Iniciando notificación para: {nombre}")
    print(f"[NOTIFICACION] 📊 Versión anterior: {empleados_version}")
    
    with empleados_lock:
        empleados_version += 1
        ultimo_cambio = {
            'tipo': 'nuevo',
            'empleado': {
                'nombre': nombre,
                'email': email,
                'jornada': jornada,
                'horas': horas,
                'estado': estado
            }
        }
        print(f"[NOTIFICACION] 📊 Nueva versión: {empleados_version}")
        print(f"[NOTIFICACION] 📦 Ultimo cambio: {ultimo_cambio}")
    
    print(f"[NOTIFICACION] ✅ Notificación completada para: {nombre}")

def notificar_empleado_actualizado(email, horas, estado):
    """Llama esto cuando ACTUALICES las horas/estado de un empleado"""
    global empleados_version, ultimo_cambio
    
    with empleados_lock:
        empleados_version += 1
        ultimo_cambio = {
            'tipo': 'actualizado',
            'empleado': {
                'email': email,
                'horas': horas,
                'estado': estado
            }
        }
    print(f"🔔 Notificado actualización: {email} - {horas}h - {estado}")