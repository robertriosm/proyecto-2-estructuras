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
                personas_en_casa: str,
                mascotas_antes: bool,
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
            WHERE a.username = $username1 AND b.disponibilidad = $dispo1 
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

        # asignarle casa ------------------------------------
        if tipo_vivienda == '1':
            tipo_vivienda = 'Grande'
        else:
            tipo_vivienda = 'Pequena'
        
        tiene_jardin = str(tiene_jardin)
        
        graph.run(
            """
            MATCH (a:Persona), (b:Casa)
            WHERE a.username = $username1 AND b.tamano = $tipo AND b.tiene_jardin = toBoolean($jardin)
            CREATE (a)-[r:VIVE_EN]->(b)
            """,
            username1=username, tipo=tipo_vivienda, jardin = tiene_jardin
        )

        # asignarle mascotas que puede manejar ------------------------------------
        if not mascotas_antes and personas_en_casa > 3:
            graph.run(
                """
                match (n:Persona), (c:Caracteristicas)
                where n.username=$username1 and c.entrenada=toBoolean(false) or c.requiere_entrenamiento=toBoolean(false)
                create (n)-[r:PUEDE_CON]->(c)
                """, username1=username
            )
        elif not mascotas_antes and personas_en_casa <= 3:
            graph.run(
                """
                match (n:Persona), (c:Caracteristicas)
                where n.username=$username1 and c.entrenada=toBoolean(false) and c.requiere_entrenamiento=toBoolean(false)
                create (n)-[r:PUEDE_CON]->(c)
                """, username1=username
            )
        elif mascotas_antes and personas_en_casa > 3:
            graph.run(
                """
                match (n:Persona), (c:Caracteristicas)
                where n.username=$username1 and c.entrenada=toBoolean(false) and c.requiere_entrenamiento=toBoolean(false)
                create (n)-[r:PUEDE_CON]->(c)
                """, username1=username
            )
        elif mascotas_antes and personas_en_casa <= 3:
            graph.run(
                """
                match (n:Persona), (c:Caracteristicas)
                where n.username=$username1 and c.entrenada=toBoolean(false) and c.requiere_entrenamiento=toBoolean(true)
                create (n)-[r:PUEDE_CON]->(c)
                """, username1=username, 
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
    username = user.get('n').get('username')
    try:
        graph.run("""
            MATCH (n:Persona {username: $username1})
            SET n.loged = false
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
            casa = 'Grande'
            graph.run(
                """
                MATCH (a:Mascota), (b:Especie), (c:Casa)
                WHERE a.petusername = $petusername1 AND b.tamano = $tipo AND b.especie = $especie1 AND c.tamano = $casa1 AND c.tiene_jardin = toBoolean('true')
                CREATE (a)-[r:ES_UN]->(b)
                CREATE (a)-[re:NECESITA_VIVIR_EN]->(c);
                """,
                petusername1=petusername, especie1=especie, tipo=tamano, casa1=casa
            )
        elif tamano == '2':
            tamano = 'Mediano'
            casa = 'Grande'
            graph.run(
                """ 
                MATCH (a:Mascota), (b:Especie), (c:Casa)
                WHERE a.petusername = $petusername1 AND b.tamano = $tipo AND b.especie = $especie1 AND c.tamano = $casa1
                CREATE (a)-[r:ES_UN]->(b)
                CREATE (a)-[re:NECESITA_VIVIR_EN]->(c)
                """,
                petusername1=petusername, especie1=especie, tipo=tamano, casa1=casa
            ) 
        elif tamano == '3':
            tamano = 'Pequeno'
            casa = 'Pequena'
            graph.run(
                """
                MATCH (a:Mascota), (b:Especie), (c:Casa)
                WHERE a.petusername = $petusername1 AND b.tamano = $tipo AND b.especie = $especie1 AND c.tamano = $casa1
                CREATE (a)-[r:ES_UN]->(b)
                CREATE (a)-[re:NECESITA_VIVIR_EN]->(c)
                """,
                petusername1=petusername, especie1=especie, tipo=tamano, casa1=casa
            )

        

        # asignarle caracter ------------------------------------
        requiere_entrenamiento = str(requiere_entrenamiento)
        entrenada = str(entrenada)

        if caracter == '1':
            caracter1 = 'Activo'
            caracter2 = 'Muy activo'
        else:
            caracter1 = 'Muy sedentaria'
            caracter2 = 'Sedentaria'

        caracter3 = 'Normal'
        
        graph.run(
            """
            MATCH (a:Mascota), (b:Personalidad)
            WHERE a.petusername = $petusername1 AND (b.personalidad = $caracter11 OR b.personalidad = $caracter12 OR b.personalidad = $caracter13)
            CREATE (a)-[r:PARECIDO_A]->(b)
            """,
            petusername1=petusername, caracter11=caracter1, caracter12=caracter2, caracter13=caracter3
        )

        # asignarle si requiere o esta entrenada para vincular con usuarios
        graph.run(
            """
            MATCH (a:Mascota), (b:Caracteristicas)
            WHERE a.petusername = $petusername1
            AND (b.entrenada = toBoolean($entrenada1) AND b.requiere_entrenamiento = toBoolean($requiere))
            CREATE (a)-[r:HA_SIDO]->(b)
            """,
            petusername1=petusername, entrenada1=str(entrenada), requiere = str(requiere_entrenamiento)
        )

        # asignarle la disponibilidad del dueno en base a su independencia
        if independencia <= 2:
            indep = 'Muy disponible'
            indep2 = ''
            indep3 = ''
            indep4 = ''
            indep5 = ''
        elif independencia <= 4:
            indep = 'Muy disponible'
            indep2 = 'Disponible'
            indep3 = ''
            indep4 = ''
            indep5 = ''
        elif independencia <= 6:
            indep = 'Muy disponible'
            indep2 = 'Disponible'
            indep3 = 'Normal'
            indep4 = ''
            indep5 = ''
        elif independencia <= 8:
            indep = 'Muy disponible'
            indep2 = 'Disponible'
            indep3 = 'Normal'
            indep4 = 'Poca disponible'
            indep5 = '' 
        elif independencia <= 10:
            indep = 'Muy disponible'
            indep2 = 'Disponible'
            indep3 = 'Normal'
            indep4 = 'Poca disponible'
            indep5 = 'Muy poco disponible' 
            
        graph.run(
                """
                MATCH (a:Mascota), (b:Disponibilidad)
                WHERE a.petusername = $petusername1
                AND (b.disponibilidad = $indep1 OR b.disponibilidad = $indep12 OR b.disponibilidad = $indep13 OR b.disponibilidad = $indep14 OR b.disponibilidad = $indep15)
                CREATE (a)-[r:NECESITA_DISPONIBILIDAD]->(b)
                """,
                petusername1=petusername,
                indep1=indep,
                indep12=indep2,
                indep13=indep3,
                indep14=indep4,
                indep15=indep5,
            )

        print('\nMascota registrada\n')

    except Exception as e:
        print('\nError al registrar mascota.\n')
        print(e)



# ------------------------------------ FUNCION CON EL ALGORITMO PARA HACER LA RECOMENDACION ------------------------------------
def search_ideal_pet(user: dict, graph: Graph):
    result = []
    username = user.get('n').get('username')
    cursor = graph.run(
        """
        MATCH (p:Persona{username:$username1})-[:VIVE_EN]->(m)<-[:NECESITA_VIVIR_EN]-(mascotas)
        RETURN mascotas
        """, username1=username
    )
    result.extend(cursor.data())
    cursor = graph.run(
        """
        MATCH (p:Persona{username:$username1})-[:PUEDE_CON]->(m)<-[:HA_SIDO]-(mascotas)
        RETURN mascotas
        """, username1=username
    )
    result.extend(cursor.data())
    cursor = graph.run(
        """
        MATCH (p:Persona{username:$username1})-[:SE_ENCUENTRA]->(m)<-[:NECESITA_DISPONIBILIDAD]-(mascotas)
        RETURN mascotas
        """, username1=username
    )
    result.extend(cursor.data())
    cursor = graph.run(
        """
        MATCH (p:Persona{username:$username1})-[:ES]->(m)<-[:PARECIDO_A]-(mascotas)
        RETURN mascotas
        """, username1=username
    )
    result.extend(cursor.data())
    return result

# ------------------------------------ FUNCION PARA DESHABILITAR DE LA RECOMENDACION A UNA MASCOTA QUE HA SIDO ADOPTADA ------------------------------------
def disable_pet(user: dict, petusername: str, graph: Graph):
    try:
        cursor = graph.run("MATCH (m:Mascota {petusername: $username1}) RETURN m",username1=petusername)
        adoptada = bool(cursor.data()[0].get('m').get('adoptada'))
        if adoptada == False:
            try:
                cursor = graph.run('MATCH (n:Mascota {petusername:$petusername1}) RETURN n;', petusername1=petusername)
                username = user.get('n').get('username')
                graph.run("""
                MATCH (n:Mascota {petusername:$petusername1}), (p:Persona {username:$username1})
                SET n.adoptada = true
                CREATE (n)-[r:ADOPTADO_POR]->(p)
                """, petusername1=petusername, username1=username)
                print("Felicidades!!! Se ha adoptado a la mascota.")
            except Exception as e:
                print(e)
        else:
            print('La mascota ya ha sido adoptada.')
    except Exception as e:
        print(e)
