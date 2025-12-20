import sys, os
import platform
import cv2
import core.detection.detection as detection

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

IS_RASPBERRY = platform.machine().startswith('arm') or platform.machine().startswith('aarch')

if IS_RASPBERRY:
    from gpiozero import Button, LED
else:
    # Clases simuladas para Windows/PC
    class LED:
        def __init__(self, pin):
            self.pin = pin
            self.state = False
        def on(self):
            self.state = True
            print(f"💡 LED {self.pin} encendido")
        def off(self):
            self.state = False
            print(f"💡 LED {self.pin} apagado")
    class Button:
        def __init__(self, pin, pull_up=True):
            self.pin = pin
            self.when_pressed = None
        def _trigger(self):
            if self.when_pressed:
                self.when_pressed()

LED_PIN = 17
BTN_DETENER = Button(23, pull_up=True)
led = LED(LED_PIN)
camIndex = 0

# Ajustar paths según plataforma
PATH_REGISTER = "/home/pi/Facial_Recognition_Raspberry/imagenes/registro/"
MODEL_PATH = "/home/pi/Facial_Recognition_Raspberry/trained_model.xml"
# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Ruta de la base de datos SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'empleados.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

xml = None
recognizer = None
names_labels = None

# Inicializar recognizer y names_labels si existe el modelo
if os.path.isfile(MODEL_PATH):
    xml = MODEL_PATH
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)
    names_labels = detection.namesToDictionary(PATH_REGISTER)