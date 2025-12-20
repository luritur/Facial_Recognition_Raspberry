from flask import current_app
from core.bd.bd_create import Empleado
from core.bd.db import db
from config import PATH_REGISTER, MODEL_PATH
import os, shutil
import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from datetime import datetime

def crear_base_datos():
    """Crea la base de datos y tablas si no existen"""
    global app
    with current_app.app_context():
        db.create_all()
        print("[DB] Base de datos creada")

def agregar_empleado(dni, nombre, email, jornada, path_image, minutos_trabajados=0, estado='out'):
    """Agrega un nuevo empleado a la DB"""
    with current_app.app_context():
        existe = Empleado.query.filter_by(dni=dni).first()
        if existe:
            print(f"[DB] ⚠️ Empleado {dni} ya existe")
            return
        nuevo = Empleado(
            dni=dni,  
            nombre=nombre,
            email=email,
            jornada=jornada,
            path_image=path_image, 
            minutos_trabajados=minutos_trabajados,
            estado=estado,
            hora_entrada=None,
            minutos_sesion_actual=0
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
        session.close()

def get_empleado_name(dni):
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
    """Retorna True si el empleado existe, False si no."""
    with current_app.app_context():
        empleado = Empleado.query.filter_by(dni=dni).first()
        return empleado is not None

def actualizar_empleado(email, minutos_trabajados=None, estado=None):
    """Actualiza minutos y/o estado de un empleado"""
    with current_app.app_context():
        emp = Empleado.query.filter_by(email=email).first()
        if not emp:
            print(f"[DB] ⚠️ Empleado {email} no encontrado")
            return
        if minutos_trabajados is not None:
            emp.minutos_trabajados = minutos_trabajados
        if estado is not None:
            emp.estado = estado
        db.session.commit()
        print(f"[DB] 🔄 Empleado {email} actualizado")

def registrar_entrada_empleado(dni):
    """Registra la entrada de un empleado (inicio de sesión de trabajo)"""
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        empleado = session.query(Empleado).filter_by(dni=dni).first()
        if not empleado:
            print(f"[DB] ⚠️ Empleado con DNI {dni} no encontrado")
            return False
        
        empleado.estado = 'working'
        empleado.hora_entrada = datetime.now()
        empleado.minutos_sesion_actual = 0
        
        session.commit()
        print(f"[DB] ✅ Entrada registrada para {empleado.nombre} a las {empleado.hora_entrada.strftime('%H:%M:%S')}")
        return True
    except Exception as e:
        print(f"[DB] ❌ Error registrando entrada: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def registrar_salida_empleado(dni):
    """Registra la salida de un empleado y calcula minutos trabajados"""
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        empleado = session.query(Empleado).filter_by(dni=dni).first()
        if not empleado:
            print(f"[DB] ⚠️ Empleado con DNI {dni} no encontrado")
            return False
        
        if empleado.hora_entrada is None:
            print(f"[DB] ⚠️ No hay registro de entrada para {empleado.nombre}")
            return False
        
        # Calcular minutos trabajados en esta sesión
        ahora = datetime.now()
        diferencia = ahora - empleado.hora_entrada
        minutos_sesion = int(diferencia.total_seconds() / 60)
        
        # Actualizar totales
        empleado.minutos_trabajados += minutos_sesion
        empleado.minutos_sesion_actual = 0
        
        # Determinar estado según si completó la jornada
        minutos_jornada = empleado.jornada * 60
        
        print(f"[DB] 📊 Minutos trabajados: {empleado.minutos_trabajados}")
        print(f"[DB] 📊 Minutos requeridos: {minutos_jornada}")
        
        if empleado.minutos_trabajados >= minutos_jornada:
            empleado.estado = 'completado'
            print(f"[DB] ✅ Jornada COMPLETADA - Estado: completado")
        else:
            empleado.estado = 'out'
            print(f"[DB] ⚠️ Jornada INCOMPLETA - Estado: out")
        
        # Limpiar hora de entrada
        empleado.hora_entrada = None
        
        session.commit()
        
        print(f"[DB] ✅ Salida registrada para {empleado.nombre}")
        print(f"[DB] ⏱️ Sesión: {minutos_sesion} min | Total: {empleado.minutos_trabajados} min")
        print(f"[DB] 📊 Estado final: {empleado.estado}")
        
        return True
    except Exception as e:
        print(f"[DB] ❌ Error registrando salida: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def actualizar_estado_empleado(dni, estado):
    """Actualiza el estado de un empleado por DNI - usado en reconocimiento"""
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        empleado = session.query(Empleado).filter_by(dni=dni).first()
        if not empleado:
            print(f"[DB] ⚠️ Empleado con DNI {dni} no encontrado")
            return False
        
        empleado.estado = estado
        session.commit()
        print(f"[DB] ✅ Estado de {empleado.nombre} ({dni}) actualizado a: {estado}")
        return True
    except Exception as e:
        print(f"[DB] ❌ Error actualizando estado: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def obtener_minutos_sesion_actual(dni):
    """Obtiene los minutos trabajados en la sesión actual"""
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        empleado = session.query(Empleado).filter_by(dni=dni).first()
        if not empleado or empleado.hora_entrada is None:
            return 0
        
        ahora = datetime.now()
        diferencia = ahora - empleado.hora_entrada
        return int(diferencia.total_seconds() / 60)
    finally:
        session.close()

def obtener_minutos_totales_actuales(dni):
    """Obtiene los minutos totales (acumulados + sesión actual)"""
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        empleado = session.query(Empleado).filter_by(dni=dni).first()
        if not empleado:
            return 0
        
        minutos_totales = empleado.minutos_trabajados
        
        # Si está trabajando, sumar sesión actual
        if empleado.estado == 'working' and empleado.hora_entrada:
            ahora = datetime.now()
            diferencia = ahora - empleado.hora_entrada
            minutos_sesion = int(diferencia.total_seconds() / 60)
            minutos_totales += minutos_sesion
        
        return minutos_totales
    finally:
        session.close()

def borrar_empleado(dni):
    # Borramos xml si era el ultimo empleado
    if os.path.isfile(MODEL_PATH):
        if len(os.listdir(PATH_REGISTER)) == 1: 
            os.remove(MODEL_PATH)
            config.xml = None
            config.recognizer = None
            config.names_labels = None
            print("⚠️ ATENCION: Has eliminado al ultimo empleado. Se ha eliminado el modelo")

    # Borramos carpeta de fotos
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