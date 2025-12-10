import os
from web import create_app, socketio
import core.gestion_empleados.gestion as gestion

# Rutas de configuración
PATH_REGISTER = "/home/pi/Facial_Recognition_Raspberry/imagenes/registro/"


# ============================================================
# INICIAR APLICACIÓN
# ============================================================

app = create_app()


gestion.socketio = socketio

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Iniciando Servidor Flask - Sistema de Reconocimiento Facial")
    print("=" * 60)
    print(f"📍 Acceso local: http://localhost:8000")
    print(f"📍 Acceso red:   http://[IP_RASPBERRY]:8000")
    print("=" * 60)

    os.makedirs(PATH_REGISTER, exist_ok=True)

    # ⚡ Aquí usamos socketio.run() en lugar de app.run()
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
