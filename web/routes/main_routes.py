from flask import render_template, Blueprint
from core.bd.bd_functions import obtener_empleados_lista


main_bp = Blueprint("main",__name__)

# RUTAS DE PÁGINAS HTML
@main_bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/registro_empleados')
def registro_empleados():
    # Cargar empleados registrados
    return render_template('registro_empleados.html', employees=obtener_empleados_lista())

@main_bp.route('/base')
def navegar():
    return render_template('base.html')

@main_bp.route('/camara')
def camara():
    return render_template('camara_directo.html')