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
                telefono,
                graph):
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


# FUNCION PARA VERIFICAR SI EL USUARIO YA EXISTE
def username_exists(username, graph):
    cursor = graph.run("MATCH (p:Persona {username: $username1}) RETURN p.username",username1=username)
    try:
        cursor.data()[0].get('p.username')
        return True
    except Exception:
        return False


# FUNCION PARA HACER UN INICIO DE SESION
def login_user(username, password, graph):
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
            return logedin

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





def pruebas(minombre, graph):
    try:
        graph.run("""
        CREATE (p:Persona{nombre:$name, 
        edad:20, 
        disponibilidadTiempo:6, 
        personalidad:"introvertido", 
        alergias:"perros", 
        estiloDeVida:"Casa",
        experiencia:4,
        presupuesto: 10,
        tipoDeVivienda:"Apartamento", 
        personasEnCasa:2, 
        ninos:TRUE, 
        telefono:12045600, 
        username:"Ye"})
        """, name=minombre,)
        print('\nUsuario creado\n')
    except Exception as e:
        print('not ok')
        print(e)












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