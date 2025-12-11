from core.bd.db import db

class Empleado(db.Model):
    __tablename__ = "empleados"

    dni = db.Column(db.String(9), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    jornada = db.Column(db.Integer, nullable=False)
    horas = db.Column(db.Float, default=0)
    estado = db.Column(db.String(20), default='out')
    path_image = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Empleado {self.nombre} ({self.email})>"
