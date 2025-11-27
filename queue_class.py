import queue

# Cola de eventos (OJO EL MAXSIZE)
frames = queue.Queue(maxsize=100)

# Cola para reconocer imagenes detectadas
detected = queue.Queue()