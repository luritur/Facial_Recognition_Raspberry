from flask_socketio import SocketIO

socketio = None  # Se asigna desde app.py

def registrar_empleado(nombre):
    empleado = {
        "nombre": nombre,
        "email": "eyeyeye@gmail.com",
        "jornada": 8,
        "horas": 0,
        "estado": "no_entro"
    }
    
    # ✅ AGREGADO: Verificar que socketio está inicializado
    if socketio is None:
        print("❌ ERROR: socketio no está inicializado")
        return empleado
    
    print(f"📡 Emitiendo evento 'nuevo_empleado': {empleado}")
    socketio.emit('nuevo_empleado', empleado, namespace='/')
    print("✅ Evento emitido")
    
    return empleado

def reconocer_empleado(email):
    if socketio is None:
        print("❌ ERROR: socketio no está inicializado")
        return
    
    print(f"📡 Emitiendo evento 'empleado_actualizado' para {email}")
    socketio.emit('empleado_actualizado', {
        "email": email,
        "horas": 8,
        "estado": "reconocido"
    }, namespace='/')
    print("✅ Evento emitido")