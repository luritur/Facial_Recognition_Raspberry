


# db.py

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from core.bd.bd_create import Empleado
from core.bd.db import db


def crear_base_datos():
    """Crea la base de datos y tablas si no existen"""
    global app
    with current_app.app_context():
        db.create_all()
        print("[DB] Base de datos creada")

def agregar_empleado(dni, nombre, email, jornada, path_image, horas=0, estado='out'):
    """Agrega un nuevo empleado a la DB"""

    with current_app.app_context():
        existe = Empleado.query.filter_by(dni=dni).first()
        if existe:
            print(f"[DB] ⚠️ Empleado {dni} ya existe")
            return
        nuevo = Empleado(
            dni = dni,  
            nombre=nombre,
            email=email,
            jornada=jornada,
            path_image = path_image, 
            horas=horas,
            estado=estado
        )
        db.session.add(nuevo)
        db.session.commit()
        print(f"[DB] ➕ Empleado {nombre} agregado")

def obtener_empleados_lista():
    """Devuelve los empleados como una lista de diccionarios"""
    empleados = []
    with current_app.app_context():
        for emp in Empleado.query.all():
            empleados.append({
                'nombre': emp.nombre,
                'dni': emp.dni,
                'email': emp.email,
                'jornada': emp.jornada,
                'estado': emp.estado,
                'horas': emp.horas
            })
    return empleados

def get_empleado_data(dni):

    with current_app.app_context():
        empleado = Empleado.query.filter_by(dni=dni).first()
        nombre = empleado.nombre
        email = empleado.email
        jornada = empleado.jornada
        return nombre, email, jornada
    
def empleado_exist(dni):
    """
    Retorna True si el empleado existe, False si no.
    """

    with current_app.app_context():
        # Busca el primer registro que coincida con el DNI
        empleado = Empleado.query.filter_by(dni=dni).first()
        
        # Si empleado no es None, es que existe
        return empleado is not None

def actualizar_empleado(email, horas=None, estado=None):
    """Actualiza horas y/o estado de un empleado"""
    with current_app.app_context():
        emp = Empleado.query.filter_by(email=email).first()
        if not emp:
            print(f"[DB] ⚠️ Empleado {email} no encontrado")
            return
        if horas is not None:
            emp.horas = horas
        if estado is not None:
            emp.estado = estado
        db.session.commit()
        print(f"[DB] 🔄 Empleado {email} actualizado")

def borrar_empleado(dni):
    """Elimina un empleado por email"""
    with current_app.app_context():
        emp = Empleado.query.filter_by(dni=dni).first()
        if not emp:
            print(f"[DB] ⚠️ Empleado {dni} no encontrado")
            return
        db.session.delete(emp)
        db.session.commit()
        print(f"[DB] ❌ Empleado {dni} eliminado")


