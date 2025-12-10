from flask_socketio import SocketIO

socketio = None # Se asigna desde app.py

def registrar_empleado(nombre):
    empleado = {
        "nombre": nombre,
        "email": "eyeyeye@gmail.com", #esto se saca de la bd
        "jornada": 8, #esto se saca de la bd
        "horas": 0,
        "estado": "no_entro"
    }
    socketio.emit('nuevo_empleado', empleado, broadcast = True)
    return empleado

def reconocer_empleado(email):
    socketio.emit('empleado_actualizado', {
        "email": email,
        "horas": 8,
        "estado": "reconocido" # de momento asi, pero hay que ver como hacer (teniendo en cuenta si ya estaba dentro o no)
    }, broadcast = True)
