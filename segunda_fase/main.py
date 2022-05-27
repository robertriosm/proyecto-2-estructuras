'''
UNIVERSIDAD DEL VALLE DE GUATEMALA
ALGORITMOS Y ESTRUCTURAS DE DATOS
FASE 2 PROYECTO 2
VISTA Y CONTROLADOR DEL SISTEMA DE RECOMENDACIONES
INTEGRANTES:
ROBERTO FRANCISCO RIOS MORALES, 20979.
NICOLE ESCOBAR 20647
NIKOLAS DIMITRIO BADANI GASDAGLIS 20092
MICAELA YATAZ 18960
'''

#from backend2 import *
import datetime
#import backend
from py2neo import Graph
from backend import *

op = ''
try:
    graphy = Graph("neo4j+s://7c20a412.databases.neo4j.io:7687", auth=("neo4j", "Tg5A8nvYBvV4m85KHiQH7Jv_K44vx0A8B2lmgU6dQdk"))
except Exception:
    print('errorcito')

fechamax = datetime.datetime(2012, 1, 1)
fechamin = datetime.datetime(1915, 1, 1)

# MENU
while op != '3':
    print(
        '\nBIENVENIDO A RECOMENDACIONES DE MASCOTAS'
        '\n1) Ingresar.'
        '\n2) Crear una cuenta.'
        '\n3) Salir.'
    )
    
    op = input('Ingrese su opcion:')

    # hacer un login    
    if op == '1':
        print('\nIngresar\n')
        user = input('Ingrese su username: ')
        while len(user) not in range(8, 21):
            print('El username debe tener entre 8 y 20 caracteres.')
            user = input('Ingrese su username: ')

        passw =  input('Ingrese su contrasena: ')
        while len(passw) not in range(8, 21):
            print('La contrasena debe tener entre 8 y 20 caracteres.')
            passw = input('Ingrese su contrasena: ')

        # falta hacer el ingreso al sistema aqui

        if login_user(user, passw):
            print('Ingreso exitoso')

    elif op == 'Ye':
        pruebas("goku", graphy)

    # crear un usuario nuevo
    elif op == '2':

        # validar username
        user = input('Ingrese un username: ')
        while (len(user) not in range(8, 21)) or username_exists(user):
            print('El username debe tener entre 8 y 20 caracteres o ya existe.')
            user = input('Ingrese su username: ')

        # validar constrasena
        passw =  input('Ingrese su contrasena: ')
        while len(passw) not in range(8, 21):
            print('La contrasena debe tener entre 8 y 20 caracteres.')
            passw = input('Ingrese su contrasena: ')

        # validar nombre
        nombre =  input('Ingrese su nombre: ')
        while len(nombre) not in range(2, 31):
            print('Su nombre debe tener entre 2 y 30 caracteres.')
            nombre = input('Ingrese su nombre: ')

        # validar apellido
        apellido =  input('Ingrese su apellido: ')
        while len(apellido) not in range(2, 31):
            print('Su apellido debe tener entre 2 y 30 caracteres.')
            apellido = input('Ingrese su apellido: ')
        
        # validar fecha de nacimiento
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
        
        # validar disponibilidad de tiempo 1-10
        ye = True
        while ye:
            dispo = input('De uno a diez, indique cual es su disponibilidad de tiempo para una mascota: ')
            try:
                dispo = int(dispo)
                if dispo in range(1,11):
                    ye = False
                else:
                    print('El valor no esta entre 1 y 10')
            except Exception as e:
                print('El valor ingresado no es un numero entero, por favor intente de nuevo')

        # validar personalidad      1=intro, 2=extro, 3=ambos
        print('Seleccione su personalidad entre las siguientes opciones:\n1) Introvertido\n2) Extrovertido\n3) Ambos')
        perso = input('Su respuesta: ')
        while perso != '1' and perso != '2' and perso != '3':
            print('No igreso una opcion correcta, por favor intente de nuevo')
            perso = input('Su respuesta: ')
        
        # validar alergias      1=pelo gato, 2=pelo perro, 3=pelo ambos, 4=ninguno
        print('Seleccione las opciones si padece de alguna:\n1) Alergia al pelo de gato\n2) Alergia al pelo de perro\n3) Alergia a ambos\n4) Ninguna')
        alergia_pelo = input('Su respuesta: ')
        while alergia_pelo != '1' and alergia_pelo != '2' and alergia_pelo != '3' and alergia_pelo != '4': 
            print('Ingreso no valido, por favor elija una opcion.')
            alergia_pelo = input('Su respuesta: ')

        # validar personas en casa      1-20
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
        
        # validar si ha tenido mascotas antes, true false
        mascotas_a = input('ha tenido mascotas antes? (escriba si o no): ').lower()
        while mascotas_a != 'si' and mascotas_a != 'no':            
            print('Ingreso no valido')
            mascotas_a = input('ha tenido mascotas antes? (escriba si o no): ').lower()
        if mascotas_a == 'si':
            mascotas_antes = True
        else:
            mascotas_antes = False
        
        # verificar si hay ninos en casa, true false
        ninos = input('hay ninos en su casa? (escriba si o no): ').lower()
        while ninos != 'si' and ninos != 'no': 
            print('Ingreso no valido')
            ninos = input('ha tenido mascotas antes? (escriba si o no): ').lower()
        if ninos == 'si':
            ninos_casa = True
        else:
            ninos_casa = False
        
        # verificar presupuesto al mes 
        ye = True
        while ye:
            try:
                presu = float(input('Indique cuanto plantea gastar en la mascota al mes: '))
                if presu > 0:
                    ye = False
            except Exception as e:
                print(e)
                print('Ingreso una cantidad menor a 0 o un ingreso no valido')
        
        # verificar vivienda, 1=grande, 2=peque
        vivienda = input('Como es su vivienda? '
        '\n1) Grande'
        '\n2) Pequena'
        '\nSu opcion: '
        )
        while vivienda != '1' and vivienda != '2':
            print('No igreso una opcion correcta, por favor intente de nuevo.')
            vivienda = input('Como es su vivienda? '
            '\n1) Grande'
            '\n2) Pequena'
            '\nSu opcion: '
            )
        
        # verificar si la casa tiene jardin, true false
        jardin = input('hay jardin en su casa? (escriba si o no): ').lower()
        while jardin != 'si' and jardin != 'no': 
            print('Ingreso no valido')
            jardin = input('hay jardin en su casa? (escriba si o no): ').lower()
        if jardin == 'si':
            jardin_casa = True
        else:
            jardin_casa = False

        # verificar el numero de telefono
        telefono = input('Ingrese un numero de telefono: ')
        while len(telefono) != 8 and not telefono.isalnum():
            print('El telefono debe tener entre 8 digitos numericos.')
            telefono = input('Ingrese un numero de telefono: ')
        
        create_user(user,
        passw,
        nombre,
        apellido,
        fecha,
        dispo,
        perso,
        alergia_pelo,
        cant_pers,
        mascotas_antes,
        ninos_casa,
        presu,
        vivienda,
        jardin_casa,
        telefono,
        graph=graphy)

    # salir de la aplicacion
    elif op == '3':
        print('Gracias por usar el programa, vuelva pronto!')
