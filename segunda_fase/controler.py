
# ------------------------------------ librerias y modulos ------------------------------------
from py2neo import Graph
from db2 import *

# ------------------------------------ iniciar conexion a db y algunos parametros de validacion ------------------------------------
op = ''
try:
    graphy = Graph("neo4j+s://7c20a412.databases.neo4j.io:7687", auth=("neo4j", "Tg5A8nvYBvV4m85KHiQH7Jv_K44vx0A8B2lmgU6dQdk"))
except Exception:
    print('errorcito')

# ------------------------------------ MENU PRINCIPAL ------------------------------------
while op != '4':
    print(
        '\nBIENVENIDO A MOVIES'
        '\n[1] crear user.'
        '\n[2] Crear pelicula.'
        '\n[3] relacionar persona-pelicula.'
        '\n[4] Salir.'
    )
    op = input('Ingrese su opcion:')


    # ------------------------------------ hacer un login ------------------------------------
    if op == '1':
        user = input('ingrese un nombre: ')
        userId = input('ingrese un id: ')
        create_user(user, userId, graph=graphy)
        print('\nusuario creado, puede revisar la db si gusta\n')

    # ------------------------------------ crear un usuario nuevo ------------------------------------
    elif op == '2':
        title = input('ingrese un nombre: ')
        movieId = input('ingrese un id: ')
        year = input('ingrese el anio: ')
        plot = input('ingrese el plot: ')
        create_movie(title, movieId, year, plot, graph=graphy)
        print('\nusuario creado, puede revisar la db si gusta\n')

    # ------------------------------------ registrar una mascota ------------------------------------
    elif op == '3':
        user = input('ingrese un nombre: ')
        userId = input('ingrese un id: ')
        create_relation(user, userId, graph=graphy)
        print('\nusuario creado, puede revisar la db si gusta\n')

    # ------------------------------------ salir del programa ------------------------------------
    elif op == '4':
        print('Gracias por usar el programa, vuelva pronto!')
