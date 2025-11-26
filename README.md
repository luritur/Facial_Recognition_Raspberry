

# link: https://gist.githz  ub.com/QurratulWidiana/29cf390403567aeb9297d6b15e5ef947
# link: https://docs.opencv.org/4.x/

# Facial_Recognition_Raspberry

# doc: https://www.raspberrypi.com/documentation/computers/camera_software.html

# guide: camera usb: https://raspberrypi-guide.github.io/electronics/using-usb-webcams

# link: configure Haar cascade opencv: https://pyimagesearch.com/2021/04/12/opencv-haar-cascades/
# link: EigenFaces recognition: https://pyimagesearch.com/2021/05/10/opencv-eigenfaces-for-face-recognition/#pyis-cta-modal

# Pasos: 
#   1.Deteccion facial 
#       1.1: 

# link: https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalcatface.xml

# link: https://github.com/austinjoyal/haar-cascade-files

#   2.Reconocimiento facial: comparar la cara con las registradas 
#       2.1: Extraer features/atributos de la cara
#       2.2: Medir distancia de cada atributo de la cara respecto a ese atributo de todas las caras guardadas


# link: https://gist.github.com/QurratulWidiana/29cf390403567aeb9297d6b15e5ef947


#       2.3: Probar threshold para encontrar el threshold adecuado
#       2.4: Si es igual o mayor al threshold, se reconoce y sino NO


#   3.El output: altavoz/web/....




# HILOS A LANZAR: 

#   1. Camara y añade a cola los frames 
#   2. Deteccion cara 
#   3. Reconocimiento cara -- if(reconocido):altavoz, break;
#   4. Mostrar resultados en web/frame



# Logica de funcionamiento: 

# HACER UN "mini csv o bd"

#   1.Si pulsas 1 vez: foto de tu cara y se guarda en carpeta de caras registradas
#   2.Si pulsas otro boton se INICIA el proceso de los hilos
#       2.1 OJO CAMARA: 15-30 frames por segundo y LIMITAR a 10 segundos MAX (ir viendo estos valores para optimizar)

#       2.2 SI pulsas PAUSA DE EMERGENCIA
#       2.3 Si pasa el tiempo y no te reconoce SE ACABA SIN RECONOCER 
#       2.4 Si pasa el tiempo y se RECONOCE: se guarda el "TIMESTAMP" de entrada/salida dependiendo de lo que sea en la BD

# SI DA TIEMPO: IMPLEMENTAR PARTE VISUAL(WEB)/ALTAVOZ


