from gpiozero import Button, LED
import threading
import queue
import time
import run
import registrar
import csv
import pandas as pd
import keyboard

# Pines BCM
LED_PIN = 17
BTN_REGISTRAR = Button(23, pull_up=True)    # aumenta frecuencia
BTN_RUN = Button(24, pull_up=True)  # disminuye frecuencia
led = LED(LED_PIN)

registered_dni_csv = pd.read_csv("registeredDNI.csv")


# Cola de eventos (OJO EL MAXSIZE)
frames = queue.Queue(maxsize=100)

# Flag para evitar que se ejecuten varias cosas a la vez
en_ejecucion = False

def ejecutar_registro():
    global en_ejecucion #global para poder cambiarlo para todo el main.py, no solo para esta función
    if en_ejecucion:
        print("Ya hay una acción en ejecución.")
        return
    #PONE EL "EN_EJECUCION" A TRUE PARA NO PODER EJECUTAR LA OTRA FUNCION (run) SI INTENTAMOS HACERLO
    en_ejecucion = True
    print("=== REGISTRANDO TRABAJADOR ===")
    registrar.registrar_foto(registered_dni_csv)
    en_ejecucion = False
    print("=== REGISTRO COMPLETADO ===")


def ejecutar_run():
    global en_ejecucion #global para poder cambiarlo para todo el main.py, no solo para esta función
    if en_ejecucion:
        print("Ya hay una acción en ejecución.")
        return
    #PONE EL "EN_EJECUCION" A TRUE PARA NO PODER EJECUTAR LA OTRA FUNCION (registro) SI INTENTAMOS HACERLO
    en_ejecucion = True
    print("=== INICIANDO RUN (10 segundos) ===")
    # Este RUN internamente crea 2 o 3 hilos (captura/detección/reconocimiento)
    run.run(frames, 10, False) #True o False es para abrir una ventana para los FRAMES
    en_ejecucion = False
    print("=== RUN COMPLETADO ===")


# Asignar callbacks simples y SIN HILOS
BTN_REGISTRAR.when_pressed = ejecutar_registro
BTN_RUN.when_pressed = ejecutar_run


# Loop principal — NO hay hilos aquí
while True:
    if keyboard.is_pressed("space"):
        break
    time.sleep(0.05)

""""
try:
    while True:
        evt = events.get()
        if evt == "UP":
            index = min(index + 1, len(freqs) - 1)
        elif evt == "DOWN":
            index = max(index - 1, 0)
        print(f"Frecuencia actual: {freqs[index]} Hz")
except KeyboardInterrupt:
    print("\nSaliendo...")
    led.off()
"""