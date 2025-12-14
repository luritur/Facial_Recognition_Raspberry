


# db.py

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from core.bd.bd_create import Empleado
from core.bd.db import db
from config import PATH_REGISTER, MODEL_PATH
import os, shutil
import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config

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
 
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        empleados = session.query(Empleado).all()
        return empleados
    except Exception as e:
        print(f"Error al obtener empleados: {e}")
        return []
    finally:
        session.close()  # Importante: cerrar la sesión

# En bd_functions.py
def get_empleado_name(dni):

    # Crear una sesión independiente sino daba error
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        empleado = session.query(Empleado).filter_by(dni=dni).first()
        if empleado:
            return empleado.nombre
        return "Desconocido"
    finally:
        session.close()
    
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

    #borramos xml si era el ultimo empleado
    #revisar que existe el xml
    if os.path.isfile(MODEL_PATH):
        if len(os.listdir(PATH_REGISTER)) == 1: 
            os.remove(MODEL_PATH)
            config.xml = None
            config.recognizer = None
            config.names_labels = None
            print("⚠️ ATENCION: Has eliminado al ultimo empleado. Se ha eliminado el modelo")


    #borramos carpeta de fotos :    
    persona_path = os.path.join(PATH_REGISTER, dni) 
    if os.path.exists(persona_path):
        shutil.rmtree(persona_path)
        print("Carpeta borrada") 
    

    with current_app.app_context():
        emp = Empleado.query.filter_by(dni=dni).first()
        if not emp:
            print(f"[DB] ⚠️ Empleado {dni} no encontrado")
            return
        db.session.delete(emp)
        db.session.commit()
        print(f"[DB] ❌ Empleado {dni} eliminado")


