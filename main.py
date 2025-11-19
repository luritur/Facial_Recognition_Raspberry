#import cv2
#
#cap = cv2.VideoCapture(0)  # Abre la cámara

#while True:
#    ret, frame = cap.read()
#    if not ret:
#        print("No se pudo leer el frame.")
#        break

#   cv2.imshow("Cámara", frame)  # Muestra el frame en una ventana llamada "Cámara" (camara/ventana)

    # Espera 1 ms y revisa si se presionó la tecla ESC (código 27)
#    if cv2.waitKey(x) & 0xFF == 27:    x=tiempo de cada frame (1000/60)
#        break

#cap.release()
#cv2.destroyAllWindows()


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


 
#Si se pulsa el BTN_REGISTRAR, se hace una foto 
def btn_registrar():
    BTN_REGISTRAR.when_pressed = registrar.registrar_foto(registered_dni_csv)


def btn_run():
    BTN_RUN.when_pressed = run.run()

# Cola de eventos


while True: 
    if(BTN_REGISTRAR.is_pressed):
        registrar.registrar_foto(registered_dni_csv)
    if(BTN_RUN.is_pressed):
        run.run()
    if(keyboard.read_key()=="space"):
        break


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