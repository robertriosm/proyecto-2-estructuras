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

# unico modulo usado de py2neo
from py2neo import Graph

# ------------------------------------ FUNCIONES PARA CONECTARSE A NEO4J ------------------------------------

# ------------------------------------ FUNCION PARA CREAR UN NUEVO USUARIO EN LA BASE DE DATOS ------------------------------------
def create_user(username: str,
                password: str,
                nombre: str,
                apellido: str,
                fecha_nacimiento: str,
                disponibilidad: str,
                personalidad: int,
                alergia: str,
                personas_en_casa: str,
                mascotas_antes: bool,
                ninos: bool,
                presupuesto: float,
                tipo_vivienda: str,
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
        personas_en_casa:toInteger($personas_en_casa1),
        mascotas_antes:toBoolean($mascotas_antes1),
        presupuesto:toFloat($presupuesto1),
        telefono:$telefono1,
        loged:FALSE})
        """,
        username1=username,
        password1=password,
        nombre1=nombre, 
        apellido1=apellido,
        fecha_nacimiento1=fecha_nacimiento,
        personas_en_casa1=personas_en_casa,
        mascotas_antes1=mascotas_antes,
        presupuesto1=presupuesto,
        telefono1=telefono,
        )

        # asignarle disponibilidad ------------------------------------
        if disponibilidad <= 2:
            dispo = 'Muy poca disponibilidad'
        elif disponibilidad in range(3, 5):
            dispo = 'Poca disponibilidad'
        elif disponibilidad in range(5, 7):
            dispo = 'Normal'
        elif disponibilidad in range(7, 9):
            dispo = 'Disponible'
        elif disponibilidad > 8:
            dispo='Muy disponible'

        graph.run(
            """
            MATCH (a:Persona), (b:Disponibilidad)
            WHERE a.username = $username1 AND b.personalidad = $perso1 
            CREATE (a)-[r:SE_ENCUENTRA]->(b)
            """,
            username1=username, dispo1=dispo
        )

        # asignarle personalidad ------------------------------------
        if personalidad <= 2:
            perso = 'Muy sedentario'
        elif personalidad in range(3, 5):
            perso = 'Sedentario'
        elif personalidad in range(5, 7):
            perso = 'Normal'
        elif personalidad in range(7, 9):
            perso = 'Activo'
        elif personalidad > 8:
            perso='Muy activo'

        graph.run(
            """
            MATCH (a:Persona), (b:Personalidad)
            WHERE a.username = $username1 AND b.personalidad = $perso1 
            CREATE (a)-[r:ES]->(b)
            """,
            username1=username, perso1=perso
        )

        # asignarle alergias ------------------------------------
        if alergia == '1':
            alergia = 'pelo de gato'
        elif alergia == '2':
            alergia = 'pelo de perro'
        elif alergia == '3':
            alergia = 'ambos'
        elif alergia == '4':
            alergia = 'ninguno'

        
        graph.run(
            """
            MATCH (a:Persona), (b:Alergia)
            WHERE a.username = $username1 AND b.alergia = $alergia1
            CREATE (a)-[r:ALERGICO_A]->(b)
            """,
            username1=username, alergia1=alergia
        )

        # asignarle casa ------------------------------------
        if tipo_vivienda == '1':
            tipo_vivienda = 'Grande'
        else:
            tipo_vivienda = 'Pequena'
        
        ninos = str(ninos)
        tiene_jardin = str(tiene_jardin)
        
        graph.run(
            """
            MATCH (a:Persona), (b:Casa)
            WHERE a.username = $username1 AND b.tamano = $tipo AND b.tiene_jardin = toBoolean($jardin) AND b.tiene_ninos = toBoolean($ninos1) 
            CREATE (a)-[r:VIVE_EN]->(b)
            """,
            username1=username, tipo=tipo_vivienda, ninos1=ninos, jardin = tiene_jardin
        )

        print('\nUsuario creado\n')
        
    except Exception as e:
        print('\nError al crear este usuario\n')
        print(e)



# ------------------------------------ FUNCION PARA VERIFICAR SI EL USUARIO YA EXISTE EN LA DB ------------------------------------
def username_exists(username: str, graph: Graph):
    cursor = graph.run("MATCH (p:Persona {username: $username1}) RETURN p.username",username1=username)
    try:
        cursor.data()[0].get('p.username')
        return True
    except Exception:
        return False



# ------------------------------------ FUNCION PARA HACER UN INICIO DE SESION ------------------------------------
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
    return False, {}



# ------------------------------------ FUNCION PARA VERIFICAR SI UNA MASCOTA YA EXISTE ------------------------------------
def pet_username_exists(petusername: str, graph: Graph):
    cursor = graph.run("MATCH (m:Mascota {username: $username1}) RETURN m.petusername",username1=petusername)
    try:
        cursor.data()[0].get('m.username')
        return True
    except Exception:
        return False



# ------------------------------------ PARA HACER LOGOUT ------------------------------------
def logoutuser(user: dict, graph: Graph):
    username = user.get('username')
    try:
        graph.run("""
            MATCH (n:Persona {username: $username1})
            SET n.loged = false
            RETURN n
            """, username1=username)
    except Exception as e:
        print(e)
        print('errorcito')



# ------------------------------------ FUNCION PARA CREAR UNA NUEVA MASCOTA ------------------------------------
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
        edad:toInteger($edad1),
        independencia:toInteger($independencia1),
        adoptada:FALSE})
        """,
        petusername1=petusername,
        edad1=edad,
        independencia1=independencia,
        )

        # asignarle especie ------------------------------------
        if especie == '1':
            especie = 'Perro'
        else:
            especie = 'Gato'
        
        if tamano == '1':
            tamano = 'Grande'
        elif tamano == '2':
            tamano = 'Mediano'
        elif tamano == '3':
            tamano = 'Pequeno'
        
        graph.run(
            """
            MATCH (a:Mascota), (b:Especie)
            WHERE a.petusername = $petusername1 AND b.tamano = $tipo AND b.especie = $especie1
            CREATE (a)-[r:ES_UN]->(b)
            """,
            petusername1=petusername, especie1=especie, tipo=tamano
        )

        # asignarle require_entrenamiento, entrenada y caracter ------------------------------------
        requiere_entrenamiento = str(requiere_entrenamiento)
        entrenada = str(entrenada)

        if caracter == '1':
            caracter = 'Activa'
        else:
            caracter = 'Tranquila'
        
        graph.run(
            """
            MATCH (a:Mascota), (b:Caracteristicas)
            WHERE a.petusername = $petusername1 AND b.caracter = $caracter1 AND b.entrenada = $entrenada1 AND b.requiere_entrenamiento = $requiere
            CREATE (a)-[r:POSEE_Y_REQUIERE]->(b)
            """,
            petusername1=petusername, caracter1=caracter, entrenada1=entrenada, requiere=requiere_entrenamiento
        )

        # asignarle condiciones ------------------------------------
        if condiciones == '1':
            condicion = 'Lesion'
        elif condiciones == '2':
            condicion = 'Desnutricion'
        elif condiciones == '3':
            condicion = 'Ambas'
        else:
            condicion = 'Ninguna'

        graph.run(
            """
            MATCH (a:Mascota), (b:Condiciones)
            WHERE a.petusername = $petusername1 AND b.condicion = $condicion1
            CREATE (a)-[r:POSEE_Y_REQUIERE]->(b)
            """,
            petusername1=petusername, condicion1=condicion
        )

        print('\nMascota registrada\n')
    except Exception as e:
        print('\nError al registrar mascota.\n')
        print(e)



# ------------------------------------ FUNCION CON EL ALGORITMO PARA HACER LA RECOMENDACION ------------------------------------
def search_ideal_pet(user: dict):
    return [{}]



# ------------------------------------ FUNCION PARA DESHABILITAR DE LA RECOMENDACION A UNA MASCOTA QUE HA SIDO ADOPTADA ------------------------------------
def disable_pet(user: dict, petusername: str, graph: Graph):
    cursor = graph.run('MATCH (n:Mascota {petusername:$petusername1}), RETURN n;', petusername1=petusername)
    adoptada = cursor.data()[0].get('n.adoptada')
    if adoptada == 'false':
        try:
            username = user.get('p.username')
            graph.run("""
            MATCH (n:Mascota {petusername:$petusername1}), (p:Persona {username:$username1})
            SET n.adoptada = true
            CREATE (n)-[r:ADOPTADO_POR]->(p)
            """, petusername1=petusername, username1=username)
            print("Felicidades!!! Se ha adoptado a la mascota.")
        except Exception as e:
            print(e)
            print("No se encontro la mascota ingresada, pruebe de nuevo.")
    else:
        print('La mascota ya ha sido adoptada.')
