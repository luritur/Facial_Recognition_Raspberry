import queue

# Cola de eventos (OJO EL MAXSIZE)
frames = queue.Queue(maxsize=100)

# Cola para reconocer imagenes detectadas
detected = queue.Queue()

# Cola para mostrar frames 
show_queue = queue.Queue(maxsize=1) #maxsize = 1 porque mostramos el ultimo frame