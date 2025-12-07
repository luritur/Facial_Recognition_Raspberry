import queue
import threading

# Cola de eventos (OJO EL MAXSIZE)
frames = queue.Queue(maxsize=100)

# Cola para reconocer imagenes detectadas
detected = queue.Queue(maxsize=100)

# Cola para mostrar frames 
show_queue = queue.Queue(maxsize=1) #maxsize = 1 porque mostramos el ultimo frame

stop_detection = threading.Event()
stop_recognition = threading.Event()

# ✅ Lock para proteger el acceso al modelo durante re-entrenamiento
model_lock = threading.Lock()