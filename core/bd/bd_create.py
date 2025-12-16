from core.bd.db import db
from datetime import datetime

class Empleado(db.Model):
    __tablename__ = "empleados"

    dni = db.Column(db.String(9), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    jornada = db.Column(db.Integer, nullable=False)  # Horas de jornada (4, 6, 8)
    minutos_trabajados = db.Column(db.Integer, default=0)  # Total acumulado en minutos
    estado = db.Column(db.String(20), default='out')  # 'out', 'working', 'completado'
    path_image = db.Column(db.String, nullable=False)
    
    # Nuevos campos para tracking de sesión
    hora_entrada = db.Column(db.DateTime, nullable=True)  # Timestamp de entrada
    minutos_sesion_actual = db.Column(db.Integer, default=0)  # Minutos de la sesión actual

    def __repr__(self):
        return f"<Empleado {self.nombre} ({self.email})>"
    
    def get_progreso_porcentaje(self):
        """Calcula el porcentaje de progreso basado en minutos trabajados"""
        minutos_jornada = self.jornada * 60
        porcentaje = min((self.minutos_trabajados / minutos_jornada) * 100, 100)
        return round(porcentaje, 1)
    
    def get_horas_formateadas(self):
        """Convierte minutos trabajados a formato HH:MM"""
        horas = self.minutos_trabajados // 60
        minutos = self.minutos_trabajados % 60
        return f"{horas}h {minutos}m"
    
    def ha_completado_jornada(self):
        """Verifica si el empleado ha completado su jornada"""
        minutos_jornada = self.jornada * 60
        return self.minutos_trabajados >= minutos_jornada