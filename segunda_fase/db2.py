
# unico modulo usado de py2neo
from py2neo import Graph

# ------------------------------------ FUNCIONES PARA CONECTARSE A NEO4J ------------------------------------

# ------------------------------------ FUNCION PARA CREAR UN NUEVO USUARIO EN LA BASE DE DATOS ------------------------------------
def create_user(name: str,
                userID: str,
                graph: Graph):
    try:
        graph.run("""
        CREATE (u:User{
        name:$name1,
        userId:$userID1})
        """,
        name1=name,
        userID1=userID
        )
        print('\nUsuario creado\n')
        
    except Exception as e:
        print('\nError al crear este nodo\n')
        print(e)


# ------------------------------------ FUNCION PARA CREAR UN NUEVA PELICULA EN LA BASE DE DATOS ------------------------------------

def create_movie(title: str,
                movieID: str,
                year: int,
                plot: str,
                graph: Graph):
    try:
        graph.run("""
        CREATE (m:Movie{
        title:$title1,
        year:$year1,
        plot:$plot1,
        movieId:$movieId1})
        """,
        title1= title,
        movieID1= movieID,
        year1= year,
        plot1= plot,
        )
        print('\pelicula creada\n')
        
    except Exception as e:
        print('\nError al crear este nodo\n')
        print(e)


# ------------------------------------ FUNCION PARA CREAR UN NUEVO RATE EN LA BASE DE DATOS ------------------------------------

def create_relation(userID: str, movieID: str, timeStamp: str, rating: str, graph: Graph):
    try:
        graph.run("""
            MERGE (u:User{userId: $userID1})
            MERGE (m:Movie{movieId: $movieID1})
            MERGE (u)-[r:RATED]->(m)
            SET r.rating = $rating1
            SET r.timeStamp = $timeStamp1
            """,
            userID1= userID,
            movieID1= movieID,
            timeStamp1= timeStamp,
            rating1= rating,
        )
    except Exception as e:
        print('\nError al crear este nodo\n')
        print(e)  