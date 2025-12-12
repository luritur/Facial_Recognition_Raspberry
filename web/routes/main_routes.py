from flask import Flask, render_template, Blueprint
import os
from core.bd.bd_functions import obtener_empleados_lista

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
   
    return render_template('registro_empleados.html', employees=obtener_empleados_lista())

@main_bp.route('/base')
def navegar():
    return render_template('base.html')

@main_bp.route('/camara')
def camara():
    return render_template('camara_directo.html')