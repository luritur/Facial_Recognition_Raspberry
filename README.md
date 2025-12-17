Sistema de Registro y Fichaje con Reconocimiento Facial
Descripción general

Este proyecto consiste en un sistema de registro y control horario de empleados mediante detección y reconocimiento facial, diseñado para funcionar en tiempo real y optimizado para su ejecución en Raspberry Pi.

El sistema permite registrar empleados, reconocerlos automáticamente a través de la cámara y reflejar su estado laboral en un dashboard web actualizado en tiempo real.

Tecnologías de visión artificial

Detección facial:
Se utiliza MediaPipe, un modelo ligero y optimizado de deep learning, ampliamente empleado en sistemas embebidos y aplicaciones de visión en tiempo real.

Reconocimiento facial:
Se emplea el modelo LBPH (Local Binary Patterns Histograms), adecuado para dispositivos con recursos limitados y eficaz con imágenes de baja resolución, lo que permite mejorar el rendimiento general del sistema.

Arquitectura web

Backend: Flask

Frontend: HTML, CSS y JavaScript

El uso de JavaScript permite la actualización en tiempo real del dashboard, los registros y las notificaciones sin necesidad de recargar la página.

Funcionalidades principales
Fichaje de empleados

Dashboard que muestra una tabla con todos los empleados registrados y su estado actual:

🔴 Fuera del trabajo

🟡 Dentro del trabajo

🟢 Jornada completada

Incluye una barra de progreso que indica las horas trabajadas, actualizada en tiempo real conforme se reconoce al empleado.

Registro de empleados

Permite visualizar los empleados registrados, añadir nuevos usuarios y entrenar el modelo de reconocimiento facial con todos los empleados de forma conjunta.

Cámara en directo

Permite iniciar y detener el reconocimiento facial y muestra en tiempo real los empleados reconocidos a través de la cámara.

Arquitectura concurrente (Threads y colas)

Con el objetivo de maximizar el rendimiento y el procesamiento en tiempo real, el sistema utiliza múltiples hilos y colas, evitando un enfoque secuencial.

Registro

Hilo de cámara (t_camara)

Captura frames y guarda únicamente aquellos en los que se detecta una cara

Los frames se envían a la cola show_queue para su visualización en la web

Reconocimiento

Se utilizan tres hilos independientes:

t_camara: captura continua de frames

t_detection: detección facial sobre los frames capturados

t_recognition: reconocimiento facial usando el modelo entrenado

Colas empleadas:

frames: frames capturados por la cámara

detected: frames en los que se ha detectado una cara

show_queue: frames mostrados en la interfaz web

Este diseño permite que la cámara capture imágenes de forma continua sin bloquearse durante la detección o el reconocimiento.

Entrenamiento del modelo

Ejecutado en un hilo independiente (t_entrenar_modelo)

Permite que el sistema continúe funcionando mientras el modelo se entrena

El entrenamiento utiliza los directorios de cada empleado (DNI) como etiquetas