import threading

# Variables globales para notificar cambios
empleados_version = 0
empleados_lock = threading.Lock()
ultimo_cambio = None

# Lista de empleados (empieza vacía o con datos de prueba)
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
    """Devuelve la lista completa de empleados"""
    with empleados_lock:
        return empleados_prueba.copy()


def agregar_empleado_a_lista(nombre, email, jornada, horas=0, estado='no_entro'):
    """Agrega el empleado a la lista interna"""
    global empleados_prueba
    
    with empleados_lock:
        # Verificar si ya existe
        existe = any(emp['nombre'] == email for emp in empleados_prueba) #cambiarlo por el DNI
        if not existe:
            empleados_prueba.append({
                'nombre': nombre,
                'email': email,
                'jornada': jornada,
                'horas': horas,
                'estado': estado
            })
            print(f"[GESTION] ➕ Empleado {nombre} agregado a la lista")
        else:
            print(f"[GESTION] ⚠️ Empleado {email} ya existe")


def notificar_nuevo_empleado(nombre, email, jornada, horas=0, estado='no_entro'):
    """Llama esto cuando REGISTRES un empleado nuevo"""
    global empleados_version, ultimo_cambio
    
    print(f"[NOTIFICACION] 🔔 Iniciando notificación para: {nombre}")
    
    # PRIMERO: Agregar a la lista
    agregar_empleado_a_lista(nombre, email, jornada, horas, estado)
    
    # SEGUNDO: Notificar el cambio
    with empleados_lock:
        version_anterior = empleados_version
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
        print(f"[NOTIFICACION] 📊 Versión: {version_anterior} → {empleados_version}")
        print(f"[NOTIFICACION] 📦 Ultimo cambio: {ultimo_cambio}")
    
    print(f"[NOTIFICACION] ✅ Notificación completada para: {nombre}")


def notificar_empleado_actualizado(email, horas, estado):
    """Llama esto cuando ACTUALICES las horas/estado de un empleado"""
    global empleados_version, ultimo_cambio
    
    with empleados_lock:
        # Actualizar en la lista
        for emp in empleados_prueba:
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