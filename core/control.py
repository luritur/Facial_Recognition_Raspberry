import threading

hilos_activos = []
stop_event = threading.Event()  #flag para detener el hilo de reconocimiento cuando pulsamos el boton de detener
entrenando_modelo = False
