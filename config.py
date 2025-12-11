# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Ruta de la base de datos SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'empleados.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
