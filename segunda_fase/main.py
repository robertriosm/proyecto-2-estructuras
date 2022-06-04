'''
UNIVERSIDAD DEL VALLE DE GUATEMALA
ALGORITMOS Y ESTRUCTURAS DE DATOS
FASE 2 PROYECTO 2
VISTA Y CONTROLADOR DEL SISTEMA DE RECOMENDACIONES
INTEGRANTES:
ROBERTO FRANCISCO RIOS MORALES, 20979.
NICOLE ESCOBAR, 20647.
NIKOLAS DIMITRIO BADANI GASDAGLIS, 20092.
MICAELA YATAZ, 18960.
'''

# ------------------------------------ librerias y modulos ------------------------------------
import datetime
from py2neo import Graph
from backend import *

# ------------------------------------ iniciar conexion a db y algunos parametros de validacion ------------------------------------
op = ''
try:
    graphy = Graph("neo4j+s://7c20a412.databases.neo4j.io:7687", auth=("neo4j", "Tg5A8nvYBvV4m85KHiQH7Jv_K44vx0A8B2lmgU6dQdk"))
except Exception:
    print('errorcito')
fechamax = datetime.datetime(2012, 1, 1)
fechamin = datetime.datetime(1915, 1, 1)

# ------------------------------------ MENU PRINCIPAL ------------------------------------
while op != '4':
    print(
        '\nBIENVENIDO A RECOMENDACIONES DE MASCOTAS'
        '\n[1] Ingresar.'
        '\n[2] Crear una cuenta.'
        '\n[3] Registrar mascota.'
        '\n[4] Salir.'
    )
    op = input('Ingrese su opcion:')


    # ------------------------------------ hacer un login ------------------------------------
    if op == '1':
        print('\nIngresar\n')

        # validar el username ------------------------------------
        user = input('Ingrese su username: ')
        while len(user) not in range(8, 21):
            print('El username debe tener entre 8 y 20 caracteres.')
            user = input('Ingrese su username: ')

        # validar la contrasena ------------------------------------
        passw =  input('Ingrese su contrasena: ')
        while len(passw) not in range(8, 21):
            print('La contrasena debe tener entre 8 y 20 caracteres.')
            passw = input('Ingrese su contrasena: ')

        # llamar a la db y hacer login ------------------------------------
        is_loged, loged_user = login_user(user, passw, graphy)

        if is_loged:
            print(f'\nIngreso exitoso, Bienvenido, {user}.')
        else:
            print('\nError al ingresar, revise el username y contrasena.\n')


        # el usuario logeado ve esto: ------------------------------------
        while is_loged:
            print('\nMenu del centro de adopcion\n'
            '[1] Buscar mascotas recomendadas.\n'
            '[2] Adoptar una mascota.\n'
            '[3] Logout.'
            )
            op2 = input('Ingrese una opcion: ')

            # llamar al algoritmo de recomendacion ------------------------------------
            if op2 == '1':
                print('\n A continuacion se muestran las mascotas que coinciden con usted:\n')
                for m in search_ideal_pet(loged_user, graph=graphy):
                    print(m)

            # adoptar una mascota ------------------------------------
            elif op2 == '2':
                # validar pet-username ------------------------------------
                pet = input('Ingrese el pet-username de la mascota que le gusto: ')
                while (len(pet) not in range(8, 21)) or pet_username_exists(pet, graphy):
                    print('El pet_username debe tener entre 8 y 20 caracteres, o ya existe, pruebe de nuevo.')
                    pet = input('Ingrese el pet-username de la mascota que le gusto: ')
                
                # relacionar a la mascota con quien la adopto y deshabilitarla ------------------------------------
                disable_pet(loged_user, pet, graphy)
            
            # salir del centro de adopcion, no del programa ------------------------------------
            elif op2 == '3':
                print('\nAdios, vuelva luego.\n')
                logoutuser(loged_user, graph=graphy)
                is_loged = False


    # ------------------------------------ crear un usuario nuevo ------------------------------------
    elif op == '2':
        # validar username ------------------------------------
        user = input('Ingrese un username: ')
        while (len(user) not in range(8, 21)) or username_exists(user, graphy):
            print('El username debe tener entre 8 y 20 caracteres, o ya existe, pruebe de nuevo.')
            user = input('Ingrese su username: ')

        # validar constrasena ------------------------------------
        passw =  input('Ingrese su contrasena: ')
        while len(passw) not in range(8, 21):
            print('La contrasena debe tener entre 8 y 20 caracteres.')
            passw = input('Ingrese su contrasena: ')

        # validar nombre ------------------------------------
        nombre =  input('Ingrese su nombre: ')
        while len(nombre) not in range(2, 31):
            print('Su nombre debe tener entre 2 y 30 caracteres.')
            nombre = input('Ingrese su nombre: ')

        # validar apellido ------------------------------------
        apellido =  input('Ingrese su apellido: ')
        while len(apellido) not in range(2, 31):
            print('Su apellido debe tener entre 2 y 30 caracteres.')
            apellido = input('Ingrese su apellido: ')
        
        # validar fecha de nacimiento ------------------------------------
        ye = True
        while ye:
            try:
                fecha =  input('Ingrese su fecha de nacimiento en el siguiente formato dd-mm-yy: ')
                fecha2 = fecha.split('-')
                fecha = datetime.datetime(int(fecha2[2]), int(fecha2[1]), int(fecha2[0]))
                if fecha > fechamin and fecha < fechamax:
                    ye = False
                else:
                    print('la fecha no es congruente')
            except Exception as e:
                print(e)
                print('Error al ingresar la fecha, por favor intente de nuevo.')
        fecha = str(fecha)[:10]
        
        # validar disponibilidad de tiempo 1-10 ------------------------------------
        ye = True
        while ye:
            dispo = input('De uno a diez, indique cual es su disponibilidad de tiempo para una mascota: ')
            try:
                dispo = int(dispo)
                if dispo in range(1,11):
                    ye = False
                else:
                    print('El valor no esta entre 1 y 10.')
            except Exception as e:
                print('El valor ingresado no es un numero entero, por favor intente de nuevo.')

        # validar personalidad ------------------------------------
        print('En una escala donde 1 es extremadamente sedentario y 10 es extremadamente activo,')
        ye = True
        while ye:
            perso = input('Indique (1-10) como se clasifica: ')
            try:
                perso = int(perso)
                if perso in range(1,11):
                    ye = False
                else:
                    print('El valor no esta entre 1 y 10.')
            except Exception as e:
                print('El valor ingresado no es un numero entero, por favor intente de nuevo.')

        # validar personas en casa, entre 1-20 ------------------------------------
        ye = True
        while ye:
            try:
                cant_pers = int(input('Indique la cantidad de personas que hay en su casa: '))
                if cant_pers in range(1,21):
                    ye = False
                else:
                    print('La cantidad ingresada no esta den tro del rango 1-20.')
            except Exception as e:
                print('Ingreso no valido')
        
        # validar si ha tenido mascotas antes, true false ------------------------------------
        mascotas_a = input('Ha tenido mascotas antes? (escriba si o no): ').lower()
        while mascotas_a != 'si' and mascotas_a != 'no':
            print('Ingreso no valido')
            mascotas_a = input('Ha tenido mascotas antes? (escriba si o no): ').lower()
        if mascotas_a == 'si':
            mascotas_antes = True
        else:
            mascotas_antes = False
        
        # verificar presupuesto al mes  ------------------------------------
        ye = True
        while ye:
            try:
                presu = float(input('Indique cuanto plantea gastar en la mascota al mes: '))
                if presu > 0:
                    ye = False
            except Exception as e:
                print(e)
                print('Ingreso una cantidad menor a 0 o un ingreso no valido')
        
        # verificar vivienda, 1=grande, 2=peque ------------------------------------
        vivienda = input('Como considera su vivienda?'
        '\n[1] Grande'
        '\n[2] Pequena'
        '\nSu opcion: '
        )
        while vivienda != '1' and vivienda != '2':
            print('No igreso una opcion correcta, por favor intente de nuevo.')
            vivienda = input('Como es su vivienda? '
            '\n[1] Grande'
            '\n[2] Pequena'
            '\nSu opcion:'
            )
        
        # verificar si la casa tiene jardin, true false ------------------------------------
        jardin = input('hay jardin en su casa? (escriba si o no): ').lower()
        while jardin != 'si' and jardin != 'no': 
            print('Ingreso no valido')
            jardin = input('hay jardin en su casa? (escriba si o no): ').lower()
        if jardin == 'si':
            jardin_casa = True
        else:
            jardin_casa = False

        # verificar el numero de telefono ------------------------------------
        telefono = input('Ingrese un numero de telefono: ')
        while len(telefono) != 8 and not telefono.isalnum():
            print('El telefono debe tener entre 8 digitos numericos.')
            telefono = input('Ingrese un numero de telefono: ')
        
        # llamar a la funcion que se comunica con la db ------------------------------------
        create_user(user,
        passw,
        nombre,
        apellido,
        fecha,
        dispo,
        perso,
        cant_pers,
        mascotas_antes,
        presu,
        vivienda,
        jardin_casa,
        telefono,
        graph=graphy)

    # ------------------------------------ registrar una mascota ------------------------------------
    elif op == '3':
        # validar pet-username ------------------------------------
        pet_user = input('Ingrese un pet-username para identificar a la mascota: ')
        while (len(pet_user) not in range(8, 21)) or pet_username_exists(pet_user, graphy):
            print('El pet_username debe tener entre 8 y 20 caracteres, o ya existe, pruebe de nuevo.')
            pet_user = input('Ingrese un pet-username: ')

        # verificar especie, 1=perro, 2=gato ------------------------------------
        especie = input('Es un perro o un gato?'
        '\n[1] Perro'
        '\n[2] Gato'
        '\nSu opcion: '
        )
        while especie != '1' and especie != '2':
            print('No igreso una opcion correcta, por favor intente de nuevo.')
            especie = input('Es un perro o un gato? '
            '\n[1] Perro'
            '\n[2] Gato'
            '\nSu opcion: '
            )

        # validar edad de la mascota, entre 0-20 ------------------------------------
        ye = True
        while ye:
            try:
                edad = int(input('Indique la edad de la mascota: '))
                if edad in range(0,21):
                    ye = False
                else:
                    print('La cantidad ingresada no esta dentro del rango 0-20.')
            except Exception as e:
                print('Ingreso no valido')

        # validar el nivel de independencia de la mascota, entre 1-10 ------------------------------------
        ye = True
        while ye:
            try:
                indep = int(input('Indique el nivel de independencia de la mascota: '))
                if indep in range(1,11):
                    ye = False
                else:
                    print('La cantidad ingresada no esta dentro del rango 1-10.')
            except Exception as e:
                print('Ingreso no valido')

        # validar tamano, 1=grande, 2=mediano, 3=pequeno ------------------------------------
        if especie == '1':
            print('Seleccione el tamano del perro:\n[1] Grande\n[2] Mediano\n[3] Pequeno')
            tamano = input('Su respuesta: ')
            while tamano != '1' and tamano != '2' and tamano != '3': 
                print('Ingreso no valido, por favor elija una opcion.')
                tamano = input('Su respuesta: ')
        else:
            tamano = '3'
        
        # validar si la mascota requiere entrenamiento, true false ------------------------------------
        requiere_e = input('La mascota requiere de algun entrenamiento? (escriba si o no): ').lower()
        while requiere_e != 'si' and requiere_e != 'no':
            print('Ingreso no valido')
            requiere_e = input('La mascota requiere de algun entrenamiento? (escriba si o no): ').lower()
        if requiere_e == 'si':
            requiere_e = True
        else:
            requiere_e = False
        
        # validar si la mascota esta entrenada, true false ------------------------------------
        entrenada = input('La mascota ha recibido entrenamiento? (escriba si o no): ').lower()
        while entrenada != 'si' and entrenada != 'no':
            print('Ingreso no valido')
            entrenada = input('La mascota ha recibido entrenamiento? (escriba si o no): ').lower()
        if entrenada == 'si':
            entrenada = True
        else:
            entrenada = False
        
        # verificar caracter, 1=Activa, 2=Tranquila ------------------------------------
        caracter = input('Describiria a la mascota como activa o tranquila?'
        '\n[1] Activa'
        '\n[2] Tranquila'
        '\nSu opcion: '
        )
        while caracter != '1' and caracter != '2':
            print('No igreso una opcion correcta, por favor intente de nuevo.')
            caracter = input('Describiria a la mascota como activa o tranquila? '
            '\n[1] Activa'
            '\n[2] Tranquila'
            '\nSu opcion: '
            )

        # validar si la mascota padece de alguna condicion ------------------------------------
        print('Seleccione una opcion, ¿la mascota padece de alguna de las siguientes condiciones?'
        '\n[1] Lesiones\n[2] Desnutricion\n[3] Ambas\n[4] Ninguna')
        condicion = input('Su respuesta: ')
        while condicion != '1' and condicion != '2' and condicion != '3' and condicion != '4': 
            print('Ingreso no valido, por favor elija una opcion.')
            condicion = input('Su respuesta: ')
        

        # llamar a la funcion que se comunica con la db creando un nodo Mascota ------------------------------------
        create_pet(pet_user, especie, edad, indep, tamano, requiere_e, entrenada, caracter, graphy)

    # ------------------------------------ salir del programa ------------------------------------
    elif op == '4':
        print('Gracias por usar el programa, vuelva pronto!')
