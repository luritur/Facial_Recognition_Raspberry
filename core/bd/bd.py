# db.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app import app, db  # Importamos la app y SQLAlchemy ya inicializado

# -------------------------
# Modelo de Empleado
# -------------------------
class Empleado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    jornada = db.Column(db.Integer, nullable=False)
    horas = db.Column(db.Integer, default=0)
    estado = db.Column(db.String(50), default='no_entro')

    def __repr__(self):
        return f"<Empleado {self.nombre}>"

# -------------------------
# Funciones CRUD
# -------------------------
def crear_base_datos():
    """Crea la base de datos y tablas si no existen"""
    with app.app_context():
        db.create_all()
        print("[DB] Base de datos creada")

def agregar_empleado(nombre, email, jornada, horas=0, estado='no_entro'):
    """Agrega un nuevo empleado a la DB"""
    with app.app_context():
        existe = Empleado.query.filter_by(email=email).first()
        if existe:
            print(f"[DB] ⚠️ Empleado {email} ya existe")
            return
        nuevo = Empleado(
            nombre=nombre,
            email=email,
            jornada=jornada,
            horas=horas,
            estado=estado
        )
        db.session.add(nuevo)
        db.session.commit()
        print(f"[DB] ➕ Empleado {nombre} agregado")

def obtener_empleados():
    """Devuelve todos los empleados"""
    with app.app_context():
        return Empleado.query.all()

def actualizar_empleado(email, horas=None, estado=None):
    """Actualiza horas y/o estado de un empleado"""
    with app.app_context():
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

def borrar_empleado(email):
    """Elimina un empleado por email"""
    with app.app_context():
        emp = Empleado.query.filter_by(email=email).first()
        if not emp:
            print(f"[DB] ⚠️ Empleado {email} no encontrado")
            return
        db.session.delete(emp)
        db.session.commit()
        print(f"[DB] ❌ Empleado {email} eliminado")


# -------------------------
# Prueba rápida
# -------------------------
if __name__ == "__main__":
    crear_base_datos()
    agregar_empleado("Pepito Grillo", "pepito@example.com", 8)
    empleados = obtener_empleados()
    print("[DB] Empleados en DB:", empleados)
