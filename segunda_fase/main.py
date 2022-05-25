'''
UNIVERSIDAD DEL VALLE DE GUATEMALA
ALGORITMOS Y ESTRUCTURAS DE DATOS
FASE 2 PROYECTO 2
VISTA Y CONTROLADOR DEL SISTEMA DE RECOMENDACIONES
INTEGRANTES:
ROBERTO FRANCISCO RIOS MORALES, 20979.
pongan sus nombres aqui xd
'''

from sympy import per
from backend import *
import datetime

op = ''

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

    # crear un usuario nuevo
    elif op == '2':
        user = input('Ingrese un username: ')
        while (len(user) not in range(8, 21)) or username_exists(user):
            print('El username debe tener entre 8 y 20 caracteres o ya existe.')
            user = input('Ingrese su username: ')

        passw =  input('Ingrese su contrasena: ')
        while len(passw) not in range(8, 21):
            print('La contrasena debe tener entre 8 y 20 caracteres.')
            passw = input('Ingrese su contrasena: ')

        nombre =  input('Ingrese su nombre: ')
        while len(nombre) not in range(2, 31):
            print('Su nombre debe tener entre 2 y 30 caracteres.')
            nombre = input('Ingrese su nombre: ')

        apellido =  input('Ingrese su apellido: ')
        while len(apellido) not in range(2, 31):
            print('Su apellido debe tener entre 2 y 30 caracteres.')
            apellido = input('Ingrese su apellido: ')
        
        ye = True
        fechamax = datetime.datetime(2012, 1, 1)
        fechamin = datetime.datetime(1915, 1, 1)
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

        print('Seleccione su personalidad entre las siguientes opciones:\n1) Introvertido\n2) Extrovertido\n3) Ambos')
        perso = input('Su respuesta: ')
        while perso != '1' and perso != '2' and perso != '3':
            print('No igreso una opcion correcta, por favor intente de nuevo')
            perso = input('Su respuesta: ')

        
        alergia_pelo = input('padece de alergia al pelo de perro o gato? (escriba si o no): ').lower()
        while alergia_pelo != 'si' and alergia_pelo != 'no': 
            print('Ingreso no valido')
            alergia_pelo = input('padece de alergia al pelo? (escriba si o no): ').lower()
        if alergia_pelo == 'si':
            alergia = True
        else:
            alergia = False

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
            
        mascotas_a = input('ha tenido mascotas antes? (escriba si o no): ').lower()
        while mascotas_a != 'si' and mascotas_a != 'no':            
            print('Ingreso no valido')
            mascotas_a = input('ha tenido mascotas antes? (escriba si o no): ').lower()
        if mascotas_a == 'si':
            mascotas_antes = True
        else:
            mascotas_antes = False
        
        ninos = input('hay ninos en su casa? (escriba si o no): ').lower()
        while ninos != 'si' and ninos != 'no': 
            print('Ingreso no valido')
            ninos = input('ha tenido mascotas antes? (escriba si o no): ').lower()
        if ninos == 'si':
            ninos_casa = True
        else:
            ninos_casa = False
        
        ye = True
        while ye:
            try:
                presu = float(input('Indique cuanto plantea gastar en la mascota al mes: '))
                if presu > 0:
                    ye = False
            except Exception as e:
                print(e)
                print('Ingreso una cantidad menor a 0 o un ingreso no valido')
        
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
        
        jardin = input('hay jardin en su casa? (escriba si o no): ').lower()
        while jardin != 'si' and jardin != 'no': 
            print('Ingreso no valido')
            jardin = input('hay jardin en su casa? (escriba si o no): ').lower()
        if jardin == 'si':
            jardin_casa = True
        else:
            jardin_casa = False

        telefono = input('Ingrese un numero de telefono: ')
        while len(telefono) != 8 and not telefono.isalnum():
            print('El telefono debe tener entre 8 digitos numericos.')
            telefono = input('Ingrese un numero de telefono: ')
        
        create_user(user, 
        passw, 
        nombre, 
        apellido, 
        str(fecha), 
        str(dispo), 
        perso, 
        str(alergia), 
        str(cant_pers), 
        str(mascotas_antes), 
        str(ninos_casa), 
        str(presu), 
        vivienda, 
        str(jardin_casa), 
        telefono )
    
        print('\nUsuario creado exitosamente!')

    # salir de la aplicacion
    elif op == '3':
        print('Gracias por usar el programa, vuelva pronto!')