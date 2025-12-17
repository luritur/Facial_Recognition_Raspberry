* [33m495393b[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mBranchPuntoSeguro[m[33m, [m[1;31morigin/BranchPuntoSeguro[m[33m)[m ahora si
* [33mefaf9ee[m error de que al cambiar de pagina dejan de salir notifaccion arreglado, era problema de que el javascript no tenia la versionId correcta
* [33mc130183[m arreglo de codigo
* [33m1822160[m colores arreglados
* [33m63de74e[m se puede entrenar al modelo durante ejecucion, pero bug: reconcimiento reconoce nueva cara y la actualiza en dashboard pero no notifica en chat
* [33m7f80f9f[m el dashboard se actualiza en tiempo real, mientras el reconocimiento corre de fondo
* [33m1ad5564[m error arreglado para actualizar progressbar
* [33m52a3f73[m ultimo push funcional, todo funciona
*   [33md0accfa[m Merge branch 'BranchPuntoSeguro' of https://github.com/luritur/Facial_Recognition_Raspberry into BranchPuntoSeguro
[32m|[m[33m\[m  
[32m|[m * [33m073d1fb[m progressbar entrenamiento completamente arreglado
[32m|[m * [33m276df33[m led ya va y mensaje de entrenamiento completado fuera
* [33m|[m [33mcd8ca01[m limpieza de codigo main
[33m|[m[33m/[m  
* [33mbf4dba7[m registro+reconocimiento a la vez, pero faltan cambios del entrenamiento
* [33m4f69371[m pasar de reconocimiento a registro
* [33ma576cd0[m fps bajados y resolucion de imagen mejorada
* [33m15041b6[m parece que ya no hay mensaje fantasma en el chat de reconocimiento
* [33m44156fb[m Revert "error del mensaje raro del chat arreglado"
* [33m93da9b4[m error del mensaje raro del chat arreglado
* [33mbf19285[m popups innecesarios quitados, progressbar del modelo cuando se entrena, quedan el color, el x se ha reconocido medio bug, el tiempo de registro y los botones.
* [33mc567a2b[m varios mensajes de warnings en la web para acciones que podrian darnos errores (avisos, pasar de pagina con reconocimiento iniciado, modelo cuando no hay nadie registrado -> modelo vacio...)
* [33m71671a8[m aviso cuando cambias de pestaña con reconocimiento iniciado (podria haber dado errores)
* [33m2de713d[m se cambia el color bien, simplemente a naranja o a rojo
* [33m5542cd9[m paso a paso: volvemos a donde antes, quito error de yield y de en_ejecucion
* [33m9bf9e21[m Revert "push de todo lo de ayer, ahora mismo da un error al reconocer pero lo voy arreglando ahora"
* [33mf7bfa56[m push de todo lo de ayer, ahora mismo da un error al reconocer pero lo voy arreglando ahora
* [33m556da16[m impleentado chat y reconocimiento (no constante) detecta cada 10 segundos para detectar entrada o salida. COSAS A SOLUCIONAR:
* [33mfdb3692[m borrado de usuario y cancelar registro implementado
* [33me5aaeea[m implementacion de la bd acabada
* [33md73e939[m he seguido implementando la bd, todavia falta
* [33mbc6e7a7[m funciona y empezado la b
*   [33m7f39582[m Merge branch 'BranchPuntoSeguro' of https://github.com/luritur/Facial_Recognition_Raspberry into BranchPuntoSeguro
[34m|[m[35m\[m  
[34m|[m * [33m1849c77[m Los nuevos registros se añaden al dashboard
* [35m|[m [33m44ab95e[m error pagina cargando arreglado
[35m|[m[35m/[m  
* [33mc3ad967[m se carga la tabla del dashboar No se añade nada al registrar un nuevo usuario pero estoy cerca
* [33m806f834[m seguro
* [33mfa404f6[m branchSeguro
[35m|[m * [33me109239[m[33m ([m[1;31morigin/main[m[33m, [m[1;31morigin/HEAD[m[33m, [m[1;32mmain[m[33m)[m el dashboard sigue sin funcioanr
[35m|[m * [33m32fb43f[m push dee seguridad
[35m|[m *   [33m24b85f4[m Merge branch 'main' of https://github.com/luritur/Facial_Recognition_Raspberry
[35m|[m [1;31m|[m[1;32m\[m  
[35m|[m [1;31m|[m *   [33mef4594f[m Merge branch 'main' of https://github.com/luritur/Facial_Recognition_Raspberry
[35m|[m [1;31m|[m [1;33m|[m[1;34m\[m  
[35m|[m [1;31m|[m * [1;34m|[m [33m123f859[m[33m ([m[1;32mvueltaAPuntoSeguro[m[33m)[m SEGUIR CON EL DASHBOARD
[35m|[m * [1;34m|[m [1;34m|[m [33m35c3f56[m cambios
[35m|[m [1;34m|[m [1;34m|[m[1;34m/[m  
[35m|[m [1;34m|[m[1;34m/[m[1;34m|[m   
[35m|[m * [1;34m|[m [33m925384f[m Merge branch 'main' of https://github.com/luritur/Facial_Recognition_Raspberry
[35m|[m [1;35m|[m[1;34m\[m[1;34m|[m 
[35m|[m [1;35m|[m * [33m8420257[m 4 segundos para registrar
[35m|[m [1;35m|[m[35m/[m  
[35m|[m[35m/[m[1;35m|[m   
* [1;35m|[m [33m7e9ee02[m ahora el modelo solo se entrena al pulsar al boton del robot
[1;36m|[m * [33mdff743f[m debug y alguna cosa mas
[1;36m|[m[1;36m/[m  
* [33me9d1e10[m[33m ([m[1;32mvueltaAFuncional[m[33m, [m[1;32mBranchSeguro[m[33m)[m ERRORES CORREGIDOS: - Cuando haces registro tarda mucho porque se entrena el modelo xml en la misma funcion--> lanzar un hilo para que se entrene aparte. - el modelo NO tiene que empezar con NONE, tiene que empezar con el XML, si no hay XML entonces si empezar con NONE - Hacer que el reconocimiento dure "infinito" hasta que pulses detener - hacer que en la camara de recognition (camara en directo) salga el recuadro alrededor de la cara (frame.drow)
* [33mf56ee17[m Implementacion de servidor Arreglado errores Deteccion de cara ya funciona Reconocimiento de cara ya funciona
* [33mafcb55c[m cambios en flask, el boton + te pide datos y tal. No funciona bien
* [33m98fe1be[m vuelta a la version anterior (no hay hilos juntos)
* [33mc7013d7[m comentario
* [33ma92750f[m hay un error de empty en detection20 y la camara sigue petando, pero hay avances
* [33mb9cf30d[m algun arreglo pero sigue petando, a la tarde sigo
* [33me2e1a76[m estructura de carpetas para flask hecha + templates basicos de html
* [33ma173f12[m cambios varios, hay que acabar reconocimiento
* [33m91e00b0[m cambio: en frame_detection face ya no es lista de lista para que lbph funcione
*   [33mf1c77af[m Merge branch 'main' of https://github.com/luritur/Facial_Recognition_Raspberry
[31m|[m[32m\[m  
[31m|[m * [33mef7bc95[m cambio nombre
* [32m|[m [33mb9d352f[m arreglado frame_detection
[32m|[m[32m/[m  
* [33md497e52[m cambios varios de deteccion
*   [33m9bca555[m Merge branch 'main' of https://github.com/luritur/Facial_Recognition_Raspberry
[33m|[m[34m\[m  
[33m|[m * [33mef6a9a9[m cambios
* [34m|[m [33mebc6387[m en principio arreglado lo de los paths de registro ahora se guardaran carpetas con el nombre de la persona y dentro de la carpeta varias fotos de la persona. El modelo se entrenara con varias fotos de cada persona
[34m|[m[34m/[m  
*   [33m06828ef[m Merge branch 'main' of https://github.com/luritur/Facial_Recognition_Raspberry
[35m|[m[36m\[m  
[35m|[m * [33me743667[m parametros
* [36m|[m [33m05506f6[m mejorado
[36m|[m[36m/[m  
* [33m217571c[m changes
* [33m459d4f2[m ahora solo se guardan en registros las fotos que detecta cara
* [33m0919510[m Ahora: - los nombre se guardan asi: pedro12.jpg - los labels se añaden en el for (no se guarda pedro_1.jpg)
* [33mc1ee93c[m changes
* [33m18b2cf0[m now yes
* [33m4fb7e8e[m split corrected
* [33m859f4a2[m more changes
* [33m6f5d73b[m more changes...
* [33me613679[m changes
* [33mb3de559[m fixing errors
* [33m821c8c5[m fixing error
* [33m9584a27[m arreglado errores de modelo nulo
* [33me2d9915[m changes
* [33m69f3217[m carpetas (vacias)
* [33m1f4eacf[m la base del reconocimiento heca, queda testear y arreglar posibles fallos
* [33m8bbb96e[m empezado a implementar el reconocimiento facial con lbph. A TENER EN CUENTA: -1: como hacer para acabar con los while True de los hilos detection_run y recognition_run? -2: OJO ver realmente cuales son las dimensions (detection.py)
* [33m06bc0ed[m estructura de carpetas
* [33mcdb100d[m links
* [33m78d2e3a[m deteccion y estructura de proyecto
* [33m4eb234d[m empezar a implementar deteccion
* [33m5dcc07c[m diferentes ficheros py
* [33med28e7e[m diferentes fichero py
* [33mfa4999f[m mas cambios
* [33m005bbd3[m rutas
* [33m49bbe85[m borrar contendio de la carpeta al inicio de la funcion
* [33m0062910[m changes
* [33m12cf0b5[m changes
* [33m82483d4[m borrar frames de ejecuciones pasadas
* [33mf6a0933[m boton run GUAR