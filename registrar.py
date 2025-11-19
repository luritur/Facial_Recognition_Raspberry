
import cv2
import keyboard

def registrar_foto(dfRegisteredWorkers):
    #devolvemos True si se ha registrado correctamente
    #devolvemos False si no se ha registrado (porque ha habido un Error o porque ya estaba registrado)



    cap = cv2.VideoCapture(0) #guarda en cap 

    if(cap.open()==False):  #ns si funciona
        print ("Error al detectar camara")
        return False
    
    ret, photo = cap.read()

    if (ret==False):
        print ("Error al leer frame")
        return False
    
    cv2.imshow("Para guardar esta foto pulsa ENTER", photo)

    while(True):
        if (keyboard.read_key()=="enter"): 
            dni = input()
            if (dni not in dfRegisteredWorkers["DNI"].values):
                cv2.imwrite(f"/RegisteredPhotos/{dni}",photo)
                dfRegisteredWorkers.loc[len(dfRegisteredWorkers)] = [dni]
                dfRegisteredWorkers.to_csv("registeredDNI.csv", index=False)
                print(f"Trabajador {dni} registrado")
                return True 
            else: #si ya esta registrado
                print("El trabajador ya está registrado")
                return False 

            
