import queue
import threading

# Cola de eventos (OJO EL MAXSIZE)
frames = queue.Queue(maxsize=100)

# Cola para reconocer imagenes detectadas
detected = queue.Queue(maxsize=100)

# Cola para mostrar frames 
show_queue = queue.Queue(maxsize=1) #maxsize = 1 porque mostramos el ultimo frame


def clear_queues():
    """Vacía todas las colas de forma segura."""
    for q in (frames, detected, show_queue):
        while not q.empty():
            try:
                q.get_nowait()
            except queue.Empty:
                break