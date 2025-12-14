import os
from web import create_app
from config import Config
from core.bd.bd_functions import crear_base_datos

# Rutas de configuración
PATH_REGISTER = "/home/pi/Facial_Recognition_Raspberry/imagenes/registro/"


# ============================================================
# INICIAR APLICACIÓN
# ============================================================

app = create_app()


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Iniciando Servidor Flask - Sistema de Reconocimiento Facial")
    print("=" * 60)
    print(f"📍 Acceso local: http://localhost:8000")
    print(f"📍 Acceso red:   http://[IP_RASPBERRY]:8000")
    print("=" * 60)
    
    # Crear carpetas necesarias si no existen
    os.makedirs(PATH_REGISTER, exist_ok=True)
    # Cargar configuración desde config.py
    app.config.from_object(Config)


    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
