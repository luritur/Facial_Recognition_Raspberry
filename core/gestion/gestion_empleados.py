import threading
from core.bd.bd_functions import obtener_empleados_lista
from core.bd.bd_functions import get_empleado_name

# Variables globales para notificar cambios
empleados_version = 0
empleados_lock = threading.Lock()
ultimo_cambio = None
confidence = 0.0


def notificar_nuevo_empleado(dni, nombre, email, jornada, minutos_trabajados=0, estado='out'):
    """Llama esto cuando REGISTRES un empleado nuevo"""
    global empleados_version, ultimo_cambio
    
    print(f"[NOTIFICACION] 🔔 Iniciando notificación para: {nombre}")
    
    # Obtener datos completos del empleado recién creado desde la BD
    from core.bd.bd_functions import obtener_minutos_totales_actuales
    empleados = obtener_empleados_lista()
    empleado_data = None
    
    for emp in empleados:
        if emp.dni == dni:
            # Calcular minutos totales en tiempo real
            minutos_totales = obtener_minutos_totales_actuales(emp.dni)
            
            # Calcular progreso con minutos totales actuales
            minutos_jornada = emp.jornada * 60
            progreso = min((minutos_totales / minutos_jornada) * 100, 100)
            
            # Formatear tiempo
            horas = minutos_totales // 60
            minutos = minutos_totales % 60
            horas_formateadas = f"{horas}h {minutos}m"
            
            # Verificar si completó jornada
            jornada_completada = minutos_totales >= minutos_jornada
            
            empleado_data = {
                'nombre': emp.nombre,
                'dni': emp.dni,
                'email': emp.email,
                'jornada': emp.jornada,
                'minutos_trabajados': emp.minutos_trabajados,
                'minutos_totales': minutos_totales,
                'estado': emp.estado,
                'progreso': round(progreso, 1),
                'horas_formateadas': horas_formateadas,
                'jornada_completada': jornada_completada
            }
            break
    
    # Fallback: si no se encontró en BD (por timing), usar datos básicos
    if not empleado_data:
        empleado_data = {
            'nombre': nombre,
            'dni': dni,
            'email': email,
            'jornada': jornada,
            'minutos_trabajados': minutos_trabajados,
            'minutos_totales': minutos_trabajados,
            'estado': estado,
            'progreso': 0.0,
            'horas_formateadas': '0h 0m',
            'jornada_completada': False
        }
    
    # Notificar el cambio
    with empleados_lock:
        version_anterior = empleados_version
        empleados_version += 1
        ultimo_cambio = {
            'tipo': 'nuevo',
            'empleado': empleado_data
        }
        print(f"[NOTIFICACION] 📊 Versión: {version_anterior} → {empleados_version}")
        print(f"[NOTIFICACION] 📦 Ultimo cambio: {ultimo_cambio}")
    
    print(f"[NOTIFICACION] ✅ Notificación completada para: {nombre}")


def notificar_empleado_actualizado(dni, estado, confidence_param):
    """Notifica actualización de estado de un empleado"""
    global empleados_version, ultimo_cambio, confidence

    confidence = round(confidence_param, 2)

    with empleados_lock:
        # Obtener datos completos del empleado
        from core.bd.bd_functions import obtener_minutos_totales_actuales
        empleados = obtener_empleados_lista()
        empleado_data = None
        
        for emp in empleados:
            if emp.dni == dni:
                # Calcular minutos totales en tiempo real
                minutos_totales = obtener_minutos_totales_actuales(emp.dni)
                
                # Calcular progreso con minutos totales actuales
                minutos_jornada = emp.jornada * 60
                progreso = min((minutos_totales / minutos_jornada) * 100, 100)
                
                # Formatear tiempo
                horas = minutos_totales // 60
                minutos = minutos_totales % 60
                horas_formateadas = f"{horas}h {minutos}m"
                
                # Verificar si completó jornada
                jornada_completada = minutos_totales >= minutos_jornada
                
                empleado_data = {
                    'dni': emp.dni,
                    'nombre': emp.nombre,
                    'email': emp.email,
                    'jornada': emp.jornada,
                    'minutos_trabajados': emp.minutos_trabajados,
                    'minutos_totales': minutos_totales,
                    'estado': emp.estado,
                    'progreso': round(progreso, 1),
                    'horas_formateadas': horas_formateadas,
                    'jornada_completada': jornada_completada
                }
                print(f"[GESTION] 🔄 Empleado {dni} actualizado. Estado: {estado}")
                break
        
        if empleado_data:
            # Notificar el cambio
            empleados_version += 1
            ultimo_cambio = {
                'tipo': 'actualizado',
                'empleado': empleado_data
            }
            print(f"[NOTIFICACION] 🔔 Notificado actualización: {dni} - estado {estado}")


