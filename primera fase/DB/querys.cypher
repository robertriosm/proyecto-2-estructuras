// crear un usuario
CREATE (p:Persona{nombre:"Roberto Rios", edad:20, disponibilidadTiempo:6, personalidad:"introvertido", salud:"nada", estiloDeVida:"Casa", experiencia:3, presupuesto: 6, tipoDeVivienda:"Apartamento"}), (p2:Persona{nombre:"Dimitri West", edad:21, disponibilidadTiempo:3, personalidad:"introvertido", salud:"nada", estiloDeVida:"Calle", experiencia:7, presupuesto: 4, tipoDeVivienda:"Residencial"}), (p3:Persona{nombre:"Ye", edad:10, disponibilidadTiempo:10, personalidad:"extrovertido", salud:"discapacidad", estiloDeVida:"Calle", experiencia:10, presupuesto: 10, tipoDeVivienda:"Con areas verdes"}) 

// crear una mascota
CREATE (p:Mascota{edad:2, especie:6, foto:"codigo_de_foto", independencia:2, tamano:"grande", entrenamiento:TRUE, entrenado:TRUE, caracter:"tranquilo", salud:"lesiones", telefono:12345678, username:"messi10"})

// crear una relacion entre usuario->mascota

