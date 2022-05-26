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
'''
from py2neo.ogm import *
from py2neo import *
import numpy as np
import pandas as pd
from py2neo import Graph, Node, Relationship, NodeMatcher

driver = Graph("bolt://localhost:7687", auth=("neo4j","hola"))
matcher = NodeMatcher(driver)
data = pd.read_csv('Mascotas.csv', header = 0)

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
