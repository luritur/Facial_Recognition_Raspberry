from flask import Flask, render_template, Blueprint
import os


# Rutas de configuración
PATH_REGISTER = "/home/pi/Facial_Recognition_Raspberry/imagenes/registro/"


main_bp = Blueprint("main",__name__)

# ============================================================
# RUTAS DE PÁGINAS HTML
# ============================================================


@main_bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/registro_empleados')
def registro_empleados():
    # Cargar empleados registrados desde la carpeta de registro
    empleados = []
    
    if os.path.exists(PATH_REGISTER):
        for carpeta in os.listdir(PATH_REGISTER):
            carpeta_path = os.path.join(PATH_REGISTER, carpeta)
            if os.path.isdir(carpeta_path):
                # El nombre de la carpeta es el nombre del empleado
                empleados.append({
                    'name': carpeta,
                    'dni': 'N/A',  # Aquí deberías guardar el DNI en algún lado
                })
    
    return render_template('registro_empleados.html', employees=empleados)

@main_bp.route('/base')
def navegar():
    return render_template('base.html')

@main_bp.route('/camara')
def camara():
    return render_template('camara_directo.html')