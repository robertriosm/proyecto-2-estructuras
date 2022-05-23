'''
UNIVERSIDAD DEL VALLE DE GUATEMALA
ALGORITMOS Y ESTRUCTURAS DE DATOS
FASE 2 PROYECTO 2
MODELO Y BACKEND DEL SISTEMA DE RECOMENDACIONES
INTEGRANTES:
ROBERTO FRANCISCO RIOS MORALES, 20979.
pongan sus nombres aqui xd
'''

# FUNCIONES PARA CONECTARSE A NEO4J
# FUNCION PARA CREAR UN NUEVO USUARIO
def create_user(username,
                password,
                nombre,
                apellido,
                edad,
                disponibilidad,
                personalidad,
                alergia,
                personas_en_casa,
                mascotas_antes,
                ninos,
                presupuesto,
                tipo_vivienda,
                telefono):

        print(username,
                password,
                nombre,
                apellido,
                edad,
                disponibilidad,
                personalidad,
                alergia,
                personas_en_casa,
                mascotas_antes,
                ninos,
                presupuesto,
                tipo_vivienda,
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