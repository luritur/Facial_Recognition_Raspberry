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

# Pines BCM
LED_PIN = 17
BTN_REGISTRAR = Button(23, pull_up=True)    # aumenta frecuencia
BTN_RUN = Button(24, pull_up=True)  # disminuye frecuencia

led = LED(LED_PIN)


def registrar_foto():
    print("Foto registrada")

#Si se pulsa el BTN_REGISTRAR, se hace una foto 
BTN_REGISTRAR.when_pressed = registrar_foto()



BTN_RUN.when_pressed = run()

# Cola de eventos


# Lanzar hilos
#t_registrar = threading.Thread(target=watch_button, args=(BTN_UP, "UP"), daemon=True)
#t_run = threading.Thread(target=watch_button, args=(BTN_DOWN, "DOWN"), daemon=True)
#t_up.start(); t_down.start(); t_led.start()

print("Control de parpadeo del LED con dos pulsadores")
print("BTN1 (GPIO23): aumentar frecuencia | BTN2 (GPIO24): disminuir frecuencia")

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
