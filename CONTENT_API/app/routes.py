from flask import Blueprint, jsonify, request
from . import models

# Define el blueprint
routes_bp = Blueprint('routes', __name__)

# Terminología de GETS
# GET /Clase -> Obtener todos los elementos de la clase
# GET /Clase/<id> -> Obtener un elemento de la clase en base a su id
# GET /Clase/buscar/<texto> -> Buscar elementos de la clase en base a un texto
# GET /Clase/<id>/ClaseRelacionada -> Obtener elementos de la clase en base a un id de la clase relacionada por ejemplo, obtener todas las temporadas de una serie en base a su id temporadas/<id>/serie

# Terminología de POSTS
# POST /Clase -> Crear un nuevo elemento de la clase

# Terminología de DELETES
# DELETE /Clase/<id> -> Eliminar un elemento de la clase en base a su id

# -------------- Endpoints para Peliculas ------------------

# Get de todas las películas
@routes_bp.route('/peliculas', methods=['GET'])
def get_peliculas():
    peliculas = models.Pelicula.query.all()
    return jsonify([pelicula.to_dict() for pelicula in peliculas])

# Get de una película en base a su id
@routes_bp.route('/peliculas/<int:id>', methods=['GET'])
def get_pelicula(id):
    pelicula = models.Pelicula.query.get_or_404(id)
    return jsonify(pelicula.to_dict())

# Busqueda de películas en base a un texto
@routes_bp.route('/peliculas/buscar/<texto>', methods=['GET'])
def buscar_peliculas(texto):
    # Normalizar el texto de búsqueda
    texto = f"%{texto.lower()}%"
    
    # Búsqueda por título
    peliculas_titulo = models.Pelicula.query.filter(
        models.db.func.lower(models.Pelicula.titulo).like(texto)
    ).all()

    # Búsqueda por sinopsis
    peliculas_sinopsis = models.Pelicula.query.filter(
        models.db.func.lower(models.Pelicula.sinopsis).like(texto)
    ).all()

    # Búsqueda por género
    peliculas_genero = models.Pelicula.query.join(
        models.generos_contenidos
    ).join(
        models.Genero
    ).filter(
        models.db.func.lower(models.Genero.nombre).like(texto)
    ).all()

    # Búsqueda por actor o personaje
    peliculas_actores = models.Pelicula.query.join(
        models.personajes_contenidos
    ).join(
        models.Personaje
    ).join(
        models.Persona
    ).filter(
        models.db.or_(
            models.db.func.lower(models.Persona.nombre).like(texto),
            models.db.func.lower(models.Persona.apellidos).like(texto),
            models.db.func.lower(models.Personaje.nombre).like(texto)
        )
    ).all()

    # Combinar resultados eliminando duplicados
    todas_peliculas = []
    peliculas_ids = set()

    for pelicula in (peliculas_titulo + peliculas_sinopsis + peliculas_genero + peliculas_actores):
        if pelicula.id not in peliculas_ids:
            todas_peliculas.append(pelicula)
            peliculas_ids.add(pelicula.id)

    return jsonify([pelicula.to_dict() for pelicula in todas_peliculas])

#  -------------- Endpoints para Series ------------------

# Get de todas las series
@routes_bp.route('/series', methods=['GET'])
def get_series():
    series = models.Serie.query.all()
    return jsonify([serie.to_dict() for serie in series])

# Get de una serie en base a su id
@routes_bp.route('/series/<int:id>', methods=['GET'])
def get_serie(id):
    serie = models.Serie.query.get_or_404(id)
    return jsonify(serie.to_dict())

# Get de series en base a un texto
@routes_bp.route('/series/buscar/<texto>', methods=['GET'])
def buscar_series(texto):
    
    # Normalizar el texto de búsqueda
    texto = f"%{texto.lower()}%"
    
    # Búsqueda por título de serie
    series_titulo = models.Serie.query.filter(
        models.db.func.lower(models.Serie.titulo).like(texto)
    ).all()

    # Búsqueda por sinopsis
    series_sinopsis = models.Serie.query.filter(
        models.db.func.lower(models.Serie.sinopsis).like(texto)
    ).all()

    # Búsqueda por título de episodio
    series_episodios = models.Serie.query.join(
        models.Temporada
    ).join(
        models.Episodio
    ).filter(
        models.db.func.lower(models.Episodio.titulo).like(texto)
    ).all()

    # Búsqueda por género (usando el primer episodio de cada serie)
    series_genero = models.Serie.query.join(
        models.Temporada
    ).join(
        models.Episodio
    ).join(
        models.generos_contenidos
    ).join(
        models.Genero
    ).filter(
        models.db.func.lower(models.Genero.nombre).like(texto)
    ).all()

    # Búsqueda por actor o personaje
    series_actores = models.Serie.query.join(
        models.Temporada
    ).join(
        models.Episodio
    ).join(
        models.personajes_contenidos
    ).join(
        models.Personaje
    ).join(
        models.Persona
    ).filter(
        models.db.or_(
            models.db.func.lower(models.Persona.nombre).like(texto),
            models.db.func.lower(models.Persona.apellidos).like(texto),
            models.db.func.lower(models.Personaje.nombre).like(texto)
        )
    ).all()

    # Combinar resultados eliminando duplicados
    todas_series = []
    series_ids = set()

    for serie in (series_titulo + series_sinopsis + series_episodios + series_genero + series_actores):
        if serie.id not in series_ids:
            todas_series.append(serie)
            series_ids.add(serie.id)

    return jsonify([serie.to_dict() for serie in todas_series])

# Get de una serie en base a un id de episodio
@routes_bp.route('/series/<int:id>/episodio', methods=['GET'])
def get_serie_by_episodio(id):
    episodio = models.Episodio.query.get_or_404(id)
    serie = models.Serie.query.join(models.Temporada).filter(models.Temporada.id == episodio.idTemporada).first_or_404()
    return jsonify(serie.to_dict())

#  -- Endpoints para Temporadas --

# Get de todas las temporadas de una serie por el id de serie
@routes_bp.route('/temporadas/<int:id>/serie', methods=['GET'])
def get_temporadas_by_serie(id):
    serie = models.Serie.query.get_or_404(id)
    return jsonify([temporada.to_dict() for temporada in serie.temporadas])

# Get de una temporada por su id
@routes_bp.route('/temporadas/<int:id>', methods=['GET'])
def get_temporada(id):
    temporada = models.Temporada.query.get_or_404(id)
    return jsonify(temporada.to_dict_full())

# Get de la temporada por el id de un episodio
@routes_bp.route('/temporadas/<int:id>/episodio', methods=['GET'])
def get_temporada_by_episodio(id):
    temporada = models.Temporada.query.join(models.Episodio).filter(models.Episodio.id == id).first_or_404()
    return jsonify(temporada.to_dict_full())

#  -- Endpoints para Episodios --

# Get de un episodio por su id
@routes_bp.route('/episodios/<int:id>', methods=['GET'])
def get_episodio(id):
    episodio = models.Episodio.query.get_or_404(id)
    return jsonify(episodio.to_dict_full())

#  -------------- Endpoints para Personas ------------------

# Get de todas las personas
@routes_bp.route('/personas', methods=['GET'])
def get_personas():
    personas = models.Persona.query.all()
    return jsonify([persona.to_dict() for persona in personas])

# Busqueda de personas en base a un texto (nombre o apellidos)
@routes_bp.route('/personas/buscar/<texto>', methods=['GET'])
def buscar_personas(texto):
    texto = f"%{texto.lower()}%"
    personas = models.Persona.query.filter(
        models.db.or_(
            models.db.func.lower(models.Persona.nombre).like(texto),
            models.db.func.lower(models.Persona.apellidos).like(texto)
        )
    ).all()
    return jsonify([persona.to_dict() for persona in personas])

# Get de una persona en base a su id
@routes_bp.route('/personas/<int:id>', methods=['GET'])
def get_persona(id):
    persona = models.Persona.query.get_or_404(id)
    return jsonify(persona.to_dict())

#  -------------- Endpoints para Personajes ------------------

# Get de todos los personajes
@routes_bp.route('/personajes', methods=['GET'])
def get_personajes():
    personajes = models.Personaje.query.all()
    return jsonify([personaje.to_dict() for personaje in personajes])

# Busqueda de personajes en base a un texto
@routes_bp.route('/personajes/buscar/<texto>', methods=['GET'])
def buscar_personajes(texto):
    texto = f"%{texto.lower()}%"
    personajes = models.Personaje.query.filter(
        models.db.func.lower(models.Personaje.nombre).like(texto)
    ).all()
    return jsonify([personaje.to_dict() for personaje in personajes])

# Get de un personaje en base a su id
@routes_bp.route('/personajes/<int:id>', methods=['GET'])
def get_personaje(id):
    personaje = models.Personaje.query.get_or_404(id)
    return jsonify(personaje.to_dict())

#  -------------- Endpoints para Generos ------------------

# Get de todos los géneros
@routes_bp.route('/generos', methods=['GET'])
def get_generos():
    generos = models.Genero.query.all()
    return jsonify([{'id': genero.id, 'nombre': genero.nombre} for genero in generos])

# Busqueda de géneros en base a un texto
@routes_bp.route('/generos/buscar/<texto>', methods=['GET'])
def buscar_generos(texto):
    texto = f"%{texto.lower()}%"
    generos = models.Genero.query.filter(
        models.db.func.lower(models.Genero.nombre).like(texto)
    ).all()
    return jsonify([{'id': genero.id, 'nombre': genero.nombre} for genero in generos])

# Get de un género en base a su id
@routes_bp.route('/generos/<int:id>', methods=['GET'])
def get_genero(id):
    genero = models.Genero.query.get_or_404(id)
    return jsonify({'id': genero.id, 'nombre': genero.nombre})

#  -------------- Endpoints para BORRAR ------------------

@routes_bp.route('/peliculas/<int:id>', methods=['DELETE'])
def delete_pelicula(id):
    pelicula = models.Pelicula.query.get_or_404(id)
    models.db.session.delete(pelicula)
    models.db.session.commit()
    return jsonify({'message': 'Pelicula eliminada exitosamente'}), 200

@routes_bp.route('/episodios/<int:id>', methods=['DELETE'])
def delete_episodio(id):
    episodio = models.Episodio.query.get_or_404(id)
    models.db.session.delete(episodio)
    models.db.session.commit()
    return jsonify({'message': 'models.Episodio eliminado exitosamente'}), 200

@routes_bp.route('/temporadas/<int:id>', methods=['DELETE'])
def delete_temporada(id):
    temporada = models.Temporada.query.get_or_404(id)
    # Borrar todos los episodios de la temporada
    for episodio in temporada.episodios:
        models.db.session.delete(episodio)
    models.db.session.delete(temporada)
    models.db.session.commit()
    return jsonify({'message': 'Temporada eliminada exitosamente'}), 200

@routes_bp.route('/series/<int:id>', methods=['DELETE'])
def delete_serie(id):
    serie = models.Serie.query.get_or_404(id)
    # Borrar todas las temporadas y episodios de la serie
    for temporada in serie.temporadas:
        for episodio in temporada.episodios:
            models.db.session.delete(episodio)
        models.db.session.delete(temporada)
    models.db.session.delete(serie)
    models.db.session.commit()
    return jsonify({'message': 'Serie eliminada exitosamente'}), 200

@routes_bp.route('/personajes/<int:id>', methods=['DELETE'])
def delete_personaje(id):
    personaje = models.Personaje.query.get_or_404(id)
    models.db.session.delete(personaje)
    models.db.session.commit()
    return jsonify({'message': 'Personaje eliminada exitosamente'}), 200

@routes_bp.route('/personas/<int:id>', methods=['DELETE'])
def delete_persona(id):
    persona = models.Persona.query.get_or_404(id)
    # Borramos todos los personajes asociados a la persona
    for personaje in persona.personajes:
        models.db.session.delete(personaje)
    models.db.session.delete(persona)
    models.db.session.commit()
    return jsonify({'message': 'Persona eliminada exitosamente'}), 200

@routes_bp.route('/generos/<int:id>', methods=['DELETE'])
def delete_genero(id):
    genero = models.Genero.query.get_or_404(id)
    models.db.session.delete(genero)
    models.db.session.commit()
    return jsonify({'message': 'Genero eliminado exitosamente'}), 200

#  -------------- Endpoints para CREAR (BASICOS) ------------------
@routes_bp.route('/series', methods=['POST'])
def create_serie():
    data = request.get_json()
    
    # Crear la nueva serie
    nueva_serie = models.Serie(
        titulo=data['titulo'],
        sinopsis=data.get('sinopsis'),
        lanzamiento=data.get('lanzamiento')
    )
    models.db.session.add(nueva_serie)
    models.db.session.commit()
    
    # Crear la primera temporada
    nueva_temporada = models.Temporada(
        nombre='Temporada 1',
        lanzamiento=data.get('lanzamiento'),
        serie_id=nueva_serie.id
    )
    models.db.session.add(nueva_temporada)
    models.db.session.commit()
    
    # Crear el primer episodio
    nuevo_episodio = models.Episodio(
        titulo=f"{data['titulo']} Ep 1",
        duracion=data.get('duracion', 0),  # Duración por defecto si no se proporciona
        sinopsis=data.get('sinopsis', ''),
        lanzamiento=data.get('lanzamiento'),
        idTemporada=nueva_temporada.id
    )
    models.db.session.add(nuevo_episodio)
    models.db.session.commit()
    
    # Agregar géneros al primer episodio
    if 'generos' in data:
        for genero_id in data['generos']:
            genero = models.Genero.query.get_or_404(genero_id)
            nuevo_episodio.generos.append(genero)
    
    # Agregar cast al primer episodio
    if 'cast' in data:
        for personaje_id in data['cast']:
            personaje = models.Personaje.query.get_or_404(personaje_id)
            nuevo_episodio.cast.append(personaje)
    
    models.db.session.commit()
    
    return jsonify(nueva_serie.to_dict()), 201

@routes_bp.route('/temporadas', methods=['POST'])
def create_temporada():
    data = request.get_json()
    
    # Crear la nueva temporada
    nueva_temporada = models.Temporada(
        nombre=data['nombre'],
        lanzamiento=data.get('lanzamiento'),
        serie_id=data['serie_id']
    )
    models.db.session.add(nueva_temporada)
    models.db.session.commit()
    
    return jsonify(nueva_temporada.to_dict()), 201

@routes_bp.route('/episodios', methods=['POST'])
def create_episodio():
    data = request.get_json()
    
    # Crear el nuevo episodio
    nuevo_episodio = models.Episodio(
        titulo=data['titulo'],
        duracion=data.get('duracion', 0),  # Duración por defecto si no se proporciona
        sinopsis=data.get('sinopsis', ''),
        lanzamiento=data.get('lanzamiento'),
        idTemporada=data['idTemporada']
    )
    models.db.session.add(nuevo_episodio)
    models.db.session.commit()
    
    return jsonify(nuevo_episodio.to_dict_full()), 201


@routes_bp.route('/series/<int:serie_id>/generos', methods=['POST'])
def add_generos_to_serie(serie_id):
    data = request.get_json()
    serie = models.Serie.query.get_or_404(serie_id)
    
    # Obtener el primer episodio de la serie
    primer_episodio = models.Episodio.query.join(models.Temporada).filter(models.Temporada.serie_id == serie.id).order_by(models.Episodio.id).first_or_404()
    
    # Agregar géneros al primer episodio
    for genero_id in data['generos']:
        genero = models.Genero.query.get_or_404(genero_id)
        primer_episodio.generos.append(genero)
    
    models.db.session.commit()
    
    return jsonify({'message': 'Géneros agregados exitosamente'}), 200

@routes_bp.route('/series/<int:serie_id>/cast', methods=['POST'])
def add_cast_to_serie(serie_id):
    data = request.get_json()
    serie = models.Serie.query.get_or_404(serie_id)
    
    # Obtener el primer episodio de la serie
    primer_episodio = models.Episodio.query.join(models.Temporada).filter(models.Temporada.serie_id == serie.id).order_by(models.Episodio.id).first_or_404()
    
    # Agregar cast al primer episodio
    for personaje_id in data['cast']:
        personaje = models.Personaje.query.get_or_404(personaje_id)
        primer_episodio.cast.append(personaje)
    
    models.db.session.commit()
    
    return jsonify({'message': 'Cast agregado exitosamente'}), 200


@routes_bp.route('/series/<int:id>', methods=['PUT'])
def update_serie(id):
    data = request.get_json()
    serie = models.Serie.query.get_or_404(id)
    serie.titulo = data.get('titulo', serie.titulo)
    serie.sinopsis = data.get('sinopsis', serie.sinopsis)
    serie.lanzamiento = data.get('lanzamiento', serie.lanzamiento)
    models.db.session.commit()
    
    # Obtener el primer episodio de la serie
    primer_episodio = models.Episodio.query.join(models.Temporada).filter(models.Temporada.serie_id == serie.id).order_by(models.Episodio.id).first_or_404()
    
    # Actualizar géneros del primer episodio
    if 'generos' in data:
        primer_episodio.generos = []
        for genero_id in data['generos']:
            genero = models.Genero.query.get_or_404(genero_id)
            primer_episodio.generos.append(genero)
    
    # Actualizar cast del primer episodio
    if 'cast' in data:
        primer_episodio.cast = []
        for personaje_id in data['cast']:
            personaje = models.Personaje.query.get_or_404(personaje_id)
            primer_episodio.cast.append(personaje)
    
    models.db.session.commit()
    
    return jsonify(serie.to_dict()), 200


@routes_bp.route('/temporadas/<int:id>', methods=['PUT'])
def update_temporada(id):
    data = request.get_json()
    temporada = models.Temporada.query.get_or_404(id)
    temporada.nombre = data.get('nombre', temporada.nombre)
    temporada.lanzamiento = data.get('lanzamiento', temporada.lanzamiento)
    models.db.session.commit()
    return jsonify(temporada.to_dict()), 200

@routes_bp.route('/episodios/<int:id>', methods=['PUT'])
def update_episodio(id):
    data = request.get_json()
    episodio = models.Episodio.query.get_or_404(id)
    episodio.titulo = data.get('titulo', episodio.titulo)
    episodio.duracion = data.get('duracion', episodio.duracion)
    episodio.sinopsis = data.get('sinopsis', episodio.sinopsis)
    episodio.lanzamiento = data.get('lanzamiento', episodio.lanzamiento)
    models.db.session.commit()
    return jsonify(episodio.to_dict_full()), 200

@routes_bp.route('/series/<int:serie_id>/cast', methods=['PUT'])
def update_cast(serie_id):
    data = request.get_json()
    serie = models.Serie.query.get_or_404(serie_id)
    
    # Obtener el primer episodio de la serie
    primer_episodio = models.Episodio.query.join(models.Temporada).filter(models.Temporada.serie_id == serie.id).order_by(models.Episodio.id).first_or_404()
    
    # Limpiar el cast actual
    primer_episodio.cast = []
    models.db.session.commit()  # Commit the deletion first
    
    # Agregar el nuevo cast
    if 'cast' in data:
        for personaje_id in data['cast']:
            personaje = models.Personaje.query.get_or_404(personaje_id)
            primer_episodio.cast.append(personaje)
    
    try:
        models.db.session.commit()
        return jsonify({'message': 'Cast actualizado exitosamente'}), 200
    except Exception as e:
        models.db.session.rollback()
        print(f"Error updating cast: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@routes_bp.route('/series/<int:serie_id>/generos', methods=['PUT'])
def update_generos(serie_id):
    data = request.get_json()
    serie = models.Serie.query.get_or_404(serie_id)
    
    # Obtener el primer episodio de la serie
    primer_episodio = models.Episodio.query.join(models.Temporada).filter(models.Temporada.serie_id == serie.id).order_by(models.Episodio.id).first_or_404()
    
    # Limpiar los géneros actuales
    primer_episodio.generos = []
    
    # Agregar los nuevos géneros
    for genero_id in data['generos']:
        genero = models.Genero.query.get_or_404(genero_id)
        primer_episodio.generos.append(genero)
    
    models.db.session.commit()
    
    return jsonify({'message': 'Géneros actualizados exitosamente'}), 200

@routes_bp.route('/peliculas', methods=['POST'])
def create_pelicula():
    data = request.get_json()
    
    # Crear la nueva película
    nueva_pelicula = models.Pelicula(
        titulo=data['titulo'],
        duracion=data.get('duracion'),
        sinopsis=data.get('sinopsis'),
        lanzamiento=data.get('lanzamiento'),
        tipo='pelicula'
    )
    models.db.session.add(nueva_pelicula)
    models.db.session.commit()
    
    # Agregar géneros a la película
    if 'generos' in data:
        for genero_id in data['generos']:
            genero = models.Genero.query.get_or_404(genero_id)
            nueva_pelicula.generos.append(genero)
    
    # Agregar cast a la película
    if 'cast' in data:
        for personaje_id in data['cast']:
            personaje = models.Personaje.query.get_or_404(personaje_id)
            nueva_pelicula.cast.append(personaje)
    
    models.db.session.commit()
    
    return jsonify(nueva_pelicula.to_dict()), 201

@routes_bp.route('/peliculas/<int:pelicula_id>/generos', methods=['POST'])
def add_generos_to_pelicula(pelicula_id):
    data = request.get_json()
    pelicula = models.Pelicula.query.get_or_404(pelicula_id)
    
    # Agregar géneros a la película
    for genero_id in data['generos']:
        genero = models.Genero.query.get_or_404(genero_id)
        pelicula.generos.append(genero)
    
    models.db.session.commit()
    
    return jsonify({'message': 'Géneros agregados exitosamente'}), 200

@routes_bp.route('/peliculas/<int:pelicula_id>/cast', methods=['POST'])
def add_cast_to_pelicula(pelicula_id):
    data = request.get_json()
    pelicula = models.Pelicula.query.get_or_404(pelicula_id)
    
    # Agregar cast a la película
    for personaje_id in data['cast']:
        personaje = models.Personaje.query.get_or_404(personaje_id)
        pelicula.cast.append(personaje)
    
    models.db.session.commit()
    
    return jsonify({'message': 'Cast agregado exitosamente'}), 200



@routes_bp.route('/peliculas/<int:id>', methods=['PUT'])
def update_pelicula(id):
    data = request.get_json()
    pelicula = models.Pelicula.query.get_or_404(id)
    pelicula.titulo = data.get('titulo', pelicula.titulo)
    pelicula.duracion = data.get('duracion', pelicula.duracion)
    pelicula.sinopsis = data.get('sinopsis', pelicula.sinopsis)
    pelicula.lanzamiento = data.get('lanzamiento', pelicula.lanzamiento)
    models.db.session.commit()
    
    # Actualizar géneros de la película
    if 'generos' in data:
        pelicula.generos = []
        for genero_id in data['generos']:
            genero = models.Genero.query.get_or_404(genero_id)
            pelicula.generos.append(genero)
    
    # Actualizar cast de la película
    if 'cast' in data:
        pelicula.cast = []
        for personaje_id in data['cast']:
            personaje = models.Personaje.query.get_or_404(personaje_id)
            pelicula.cast.append(personaje)
    
    models.db.session.commit()
    
    return jsonify(pelicula.to_dict()), 200



@routes_bp.route('/peliculas/<int:pelicula_id>/generos', methods=['PUT'])
def update_generos_pelicula(pelicula_id):
    data = request.get_json()
    pelicula = models.Pelicula.query.get_or_404(pelicula_id)
    
    # Limpiar los géneros actuales
    pelicula.generos = []
    
    # Agregar los nuevos géneros
    for genero_id in data['generos']:
        genero = models.Genero.query.get_or_404(genero_id)
        pelicula.generos.append(genero)
    
    models.db.session.commit()
    
    return jsonify({'message': 'Géneros actualizados exitosamente'}), 200

@routes_bp.route('/peliculas/<int:pelicula_id>/cast', methods=['PUT'])
def update_cast_pelicula(pelicula_id):
    data = request.get_json()
    pelicula = models.Pelicula.query.get_or_404(pelicula_id)
    
    # Limpiar el cast actual
    pelicula.cast = []
    
    # Agregar el nuevo cast
    for personaje_id in data['cast']:
        personaje = models.Personaje.query.get_or_404(personaje_id)
        pelicula.cast.append(personaje)
    
    models.db.session.commit()
    
    return jsonify({'message': 'Cast actualizado exitosamente'}), 200





#  -------------- Endpoints para CREAR (PERSONAJES) ------------------


@routes_bp.route('/personas', methods=['POST'])
def create_persona():
    data = request.get_json()
    
    # Crear la nueva persona
    nueva_persona = models.Persona(
        nombre=data['nombre'],
        apellidos=data.get('apellidos'),
        edad=data.get('edad'),
        foto=data.get('foto')
    )
    models.db.session.add(nueva_persona)
    models.db.session.commit()
    
    return jsonify(nueva_persona.to_dict()), 201

@routes_bp.route('/personas/<int:id>', methods=['PUT'])
def update_persona(id):
    data = request.get_json()
    persona = models.Persona.query.get_or_404(id)
    persona.nombre = data.get('nombre', persona.nombre)
    persona.apellidos = data.get('apellidos', persona.apellidos)
    persona.edad = data.get('edad', persona.edad)
    persona.foto = data.get('foto', persona.foto)
    models.db.session.commit()
    return jsonify(persona.to_dict()), 200

@routes_bp.route('/personajes', methods=['POST'])
def create_personaje():
    data = request.get_json()
    
    # Crear el nuevo personaje
    nuevo_personaje = models.Personaje(
        nombre=data['nombre'],
        actor_id=data['actor_id']
    )
    models.db.session.add(nuevo_personaje)
    models.db.session.commit()
    
    return jsonify(nuevo_personaje.to_dict()), 201

@routes_bp.route('/personajes/<int:id>', methods=['PUT'])
def update_personaje(id):
    data = request.get_json()
    personaje = models.Personaje.query.get_or_404(id)
    personaje.nombre = data.get('nombre', personaje.nombre)
    personaje.actor_id = data.get('actor_id', personaje.actor_id)
    models.db.session.commit()
    return jsonify(personaje.to_dict()), 200

#  -------------- Endpoints para CREAR (GENERO) ------------------

@routes_bp.route('/generos', methods=['POST'])
def create_genero():
    data = request.get_json()
    
    # Verificar si ya existe un género con el mismo nombre
    genero_existente = models.Genero.query.filter_by(nombre=data['nombre']).first()
    if genero_existente:
        return jsonify({'message': 'El género ya existe'}), 400
    
    # Crear el nuevo género
    nuevo_genero = models.Genero(
        nombre=data['nombre']
    )
    models.db.session.add(nuevo_genero)
    models.db.session.commit()
    
    return jsonify(nuevo_genero.to_dict()), 201


@routes_bp.route('/generos/<int:id>', methods=['PUT'])
def update_genero(id):
    data = request.get_json()
    genero = models.Genero.query.get_or_404(id)
    
    # Verificar si ya existe un género con el mismo nombre
    genero_existente = models.Genero.query.filter_by(nombre=data['nombre']).first()
    if genero_existente and genero_existente.id != id:
        return jsonify({'message': 'El género ya existe'}), 400
    
    genero.nombre = data.get('nombre', genero.nombre)
    models.db.session.commit()
    return jsonify(genero.to_dict()), 200