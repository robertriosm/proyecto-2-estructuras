'''
UNIVERSIDAD DEL VALLE DE GUATEMALA
ALGORITMOS Y ESTRUCTURAS DE DATOS
FASE 2 PROYECTO 2
MODELO Y BACKEND DEL SISTEMA DE RECOMENDACIONES
INTEGRANTES:
ROBERTO FRANCISCO RIOS MORALES, 20979.
NICOLE ESCOBAR, 20647.
NIKOLAS DIMITRIO BADANI GASDAGLIS, 20092.
MICAELA YATAZ, 18960.
'''

from py2neo import Graph

# --------- FUNCIONES PARA CONECTARSE A NEO4J ---------

# FUNCION PARA CREAR UN NUEVO USUARIO EN LA BASE DE DATOS
def create_user(username: str,
                password: str,
                nombre: str,
                apellido: str,
                fecha_nacimiento: str,
                disponibilidad: str,
                personalidad: str,
                alergia: str,
                personas_en_casa: str,
                mascotas_antes: bool,
                ninos: bool,
                presupuesto: float,
                tipo_vivienda: bool,
                tiene_jardin: bool,
                telefono: str,
                graph: Graph):
    try:
        graph.run("""
        CREATE (p:Persona{username:$username1,
        password:$password1,
        nombre:$nombre1, 
        apellido:$apellido1,
        fecha_nacimiento:date($fecha_nacimiento1),
        disponibilidad:toInteger($disponibilidad1),
        personalidad:$personalidad1,
        alergia:$alergia1,
        personas_en_casa:toInteger($personas_en_casa1),
        mascotas_antes:toBoolean($mascotas_antes1),
        ninos:toBoolean($ninos1),
        presupuesto:toFloat($presupuesto1),
        tipo_vivienda:$tipo_vivienda1,
        tiene_jardin:toBoolean($tiene_jardin1),
        telefono:$telefono1,
        loged:FALSE})
        """,
        username1=username,
        password1=password,
        nombre1=nombre, 
        apellido1=apellido,
        fecha_nacimiento1=fecha_nacimiento,
        disponibilidad1=disponibilidad,
        personalidad1=personalidad,
        alergia1=alergia,
        personas_en_casa1=personas_en_casa,
        mascotas_antes1=mascotas_antes,
        ninos1=ninos,
        presupuesto1=presupuesto,
        tipo_vivienda1=tipo_vivienda,
        tiene_jardin1=tiene_jardin,
        telefono1=telefono,
        )
        print('\nUsuario creado\n')
    except Exception as e:
        print('\nError al crear este usuario\n')
        print(e)



# FUNCION PARA VERIFICAR SI EL USUARIO YA EXISTE EN LA DB
def username_exists(username: str, graph: Graph):
    cursor = graph.run("MATCH (p:Persona {username: $username1}) RETURN p.username",username1=username)
    try:
        cursor.data()[0].get('p.username')
        return True
    except Exception:
        return False



# FUNCION PARA HACER UN INICIO DE SESION
def login_user(username: str, password: str, graph: Graph):
    if username_exists(username, graph):
        cursor = graph.run("MATCH (p:Persona {username: $username1}) RETURN p.password", username1=username)
        verify = cursor.data()[0].get('p.password')
        if verify == password:
            cursor = graph.run("""
            MATCH (n:Persona {username: $username1})
            SET n.loged = true
            RETURN n
            """, username1=username)
            logedin = cursor.data()[0]
            return True, logedin
    return False, 0



# FUNCION PARA VERIFICAR SI UNA MASCOTA YA EXISTE
def pet_username_exists(petusername: str, graph: Graph):
    cursor = graph.run("MATCH (m:Mascota {username: $username1}) RETURN m.petusername",username1=petusername)
    try:
        cursor.data()[0].get('m.username')
        return True
    except Exception:
        return False



# PARA HACER LOGOUT
def logoutuser(user: dict, graph: Graph):
    username = user.get('username')
    try:
        cursor = graph.run("""
            MATCH (n:Persona {username: $username1})
            SET n.loged = false
            RETURN n
            """, username1=username)
    except Exception as e:
        print(e)
        print('errorcito')



# FUNCION PARA CREAR UNA NUEVA MASCOTA
def create_pet(petusername: str,
                especie: str,
                edad: int,
                independencia: int,
                tamano: str,
                requiere_entrenamiento: bool,
                entrenada: bool,
                caracter: str,
                condiciones: str,
                graph: Graph):
    try:
        graph.run("""
        CREATE (m:Mascota{petusername:$petusername1,
        especie:$especie1,
        edad:toInteger($edad1),
        independencia:toInteger($independencia1),
        tamano:$tamano1,
        requiere_entrenamiento1=requiere_entrenamiento,
        entrenada1=entrenada,
        caracter1=caracter,
        condiciones1=condiciones,
        adoptada:FALSE})
        """,
        petusername1=petusername,
        especie1=especie,
        edad1=edad,
        independencia1=independencia,
        tamano1=tamano,
        requiere_entrenamiento1=requiere_entrenamiento,
        entrenada1=entrenada,
        caracter1=caracter,
        condiciones1=condiciones,
        )
        print('\nMascota registrada\n')
    except Exception as e:
        print('\nError al crear este usuario\n')
        print(e)



# FUNCION CON EL ALGORITMO PARA HACER LA RECOMENDACION
def search_ideal_pet(user: dict):
    return {}



# FUNCION PARA DESHABILITAR DE LA RECOMENDACION A UNA MASCOTA ADOPTADA
def disable_pet(petusername: str, graph: Graph):
    try:
        graph.run("""
        MATCH (n:Mascota {petusername:$petusername})
        SET n.adoptada = true
        RETURN n
        """)
        print("Se ha eliminado a la mascota del registro")
    except Exception as e:
        print(e)
        print("Errorcito")















'''
UNIVERSIDAD DEL VALLE DE GUATEMALA
ALGORITMOS Y ESTRUCTURAS DE DATOS
FASE 2 PROYECTO 2
MODELO Y BACKEND DEL SISTEMA DE RECOMENDACIONES
INTEGRANTES:
ROBERTO FRANCISCO RIOS MORALES, 20979.
NICOLE ESCOBAR 20647
NIKOLAS DIMITRIO BADANI GASDAGLIS 20092
MICAELA YATAZ 18960
pongan sus nombres aqui xd

# from py2neo.ogm import *
# from py2neo import *
# import numpy as np
# import pandas as pd
# from py2neo import Graph, Node, Relationship, NodeMatcher

#driver = Graph("bolt://localhost:7687", auth=("neo4j","hola"))
#matcher = NodeMatcher(driver)
#data = pd.read_csv('Mascotas.csv', header = 0)

def dataBase():
    with open('Mascotas.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        pets = {}
        for i in csv_reader:
            pets[i[0]] = [i[0], i[1], i[2], i[3],i[4], i[5], i[6], i[7], i[8], i[9], i[10]]
            
    for j in pets:
        tipo = pets[j][0]
        nombre = pets[j][1]
        tiempo = pets[j][2]
        pelo = pets[j][3]
        actividad = pets[j][4]
        caracter = pets[j][5]
        cuidados = pets[j][6]
        entrenado = pets[j][7]
        tamano = pets[j][8]
        presupuesto = pets[j][9]
        edad = pets[j][10]
        pets[j] = Node("Mascota",tipo = pets[j][0],nombre = pets[j][1],tiempo = pets[j][2],pelo = pets[j][3],actividad = pets[j][4],caracter = pets[j][5],cuidados = pets[j][6],entrenado = pets[j][7],tamano = pets[j][8],presupuesto = pets[j][9],edad = pets[j][10])
        
# FUNCIONES PARA CONECTARSE A NEO4J
# FUNCION PARA CREAR UN NUEVO USUARIO
def create_user(username,
                password,
                nombre,
                apellido,
                fecha_nacimiento,
                disponibilidad,
                personalidad,
                alergia,
                personas_en_casa,
                mascotas_antes,
                ninos,
                presupuesto,
                tipo_vivienda,
                tiene_jardin,
                telefono):

        print(username + '\n' +
                password + '\n' +
                nombre + '\n' +
                apellido + '\n' +
                fecha_nacimiento + '\n' +
                disponibilidad + '\n' +
                personalidad + '\n' +
                alergia + '\n' +
                personas_en_casa + '\n' +
                mascotas_antes + '\n' +
                ninos + '\n' +
                presupuesto + '\n' +
                tipo_vivienda + '\n' +
                tiene_jardin + '\n' +
                telefono)

# FUNCION PARA VERIFICAR SI EL USUARIO YA EXISTE
def username_exists(username):
    # esto solo simula la verificacion, se debe hacer una verificacion real
    if username == 'yaexiste':
        return True
    return False

# FUNCION PARA HACER UN INICIO DE SESION
def login_user(username, password):
    # esto solo simula la verificacion, se debe hacer una verificacion real
    if username == 'yaexiste' and password == '12345678':
        return True
    print(username + '' + password)

# FUNCION PARA CREAR UNA NUEVA MASCOTA
def create_pet(username, 
                especie, 
                edad, 
                foto, 
                independencia, 
                tamano, 
                requiere_entrenamiento, 
                entrenada, 
                caracter, 
                condiciones, 
                contacto):
    pass

# FUNCION PARA HACER LA RECOMENDACION
def search_ideal_pet():
    pass
'''
