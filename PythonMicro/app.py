from flask import Flask, jsonify, request
from config import Config
from models import db, User
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    decode_token,
)
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from sqlalchemy.exc import IntegrityError
import logging
from logstash_formatter import LogstashFormatterV1
import pika

app = Flask(__name__)
app.config.from_object(Config)

# Configuración de JWT
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Cambia esto por una clave más segura
jwt = JWTManager(app)

db.init_app(app)

# Configuración de logging
logger = logging.getLogger('logstash-logger')
logger.setLevel(logging.INFO)
logstash_handler = logging.StreamHandler()
logstash_handler.setFormatter(LogstashFormatterV1())
logger.addHandler(logstash_handler)

# Ruta para la documentación de Swagger
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "API de Usuarios"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Función para crear un nuevo usuario
def create_user(username, email, password_hash):
    new_user = User(username=username, email=email, password_hash=password_hash)
    try:
        db.session.add(new_user)
        db.session.commit()
        logger.info(f'Usuario creado: {username}')
        return {"id": new_user.id, "nombre": new_user.username, "email": new_user.email}, 201
    except IntegrityError as e:
        db.session.rollback()
        if 'unique constraint' in str(e.orig):
            return {"error": "El usuario ya existe."}, 400
        return {"error": "Error al crear el usuario."}, 500
    finally:
        db.session.close()

@app.route('/usuarios/', methods=['GET'])
@jwt_required()
def get_users():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    users = User.query.paginate(page=page, per_page=limit, error_out=False).items
    total = User.query.count()
    logger.info(f'Usuarios obtenidos: página {page}, límite {limit}')
    return jsonify({
        'total': total,
        'page': page,
        'limit': limit,
        'users': [{'id': user.id, 'nombre': user.username, 'email': user.email} for user in users]
    })

@app.route('/usuarios/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.get(id)
    if user:
        logger.info(f'Usuario obtenido: {user.username}')
        return jsonify({
            'id': user.id,
            'nombre': user.username,
            'email': user.email,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        })
    logger.warning(f'Usuario no encontrado: ID {id}')
    return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/usuarios/', methods=['POST'])
def register_user():
    data = request.get_json()
    if 'nombre' not in data or 'email' not in data or 'clave' not in data:
        return jsonify({'error': 'Faltan datos obligatorios.'}), 400

    password_hash = generate_password_hash(data['clave'])
    result, status_code = create_user(data['nombre'], data['email'], password_hash)
    return jsonify(result), status_code

@app.route('/usuarios/actualizar', methods=['PUT'])
@jwt_required()
def update_user():
    current_user_email = get_jwt_identity()
    data = request.get_json()
    email_to_update = data.get('email')

    if current_user_email != email_to_update:
        return jsonify({'error': 'No autorizado para actualizar este usuario.'}), 403

    user = User.query.filter_by(email=email_to_update).first()
    if user:
        user.username = data.get('nombre', user.username)
        user.email = data.get('email', user.email)
        db.session.commit()
        logger.info(f'Usuario actualizado: {user.username}')
        return jsonify({
            'id': user.id,
            'nombre': user.username,
            'email': user.email,
            'updated_at': user.updated_at
        })
    logger.warning(f'Usuario no encontrado para actualizar: {email_to_update}')
    return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/usuarios/eliminar', methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user_email = get_jwt_identity()
    data = request.get_json()
    email_to_delete = data.get('email')

    if current_user_email != email_to_delete:
        return jsonify({'error': 'No autorizado para eliminar este usuario.'}), 403

    user = User.query.filter_by(email=email_to_delete).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        logger.info(f'Usuario eliminado: {user.username}')
        return jsonify({'mensaje': 'Usuario eliminado exitosamente.'}), 200
    logger.warning(f'Usuario no encontrado para eliminar: {email_to_delete}')
    return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'email' not in data or 'clave' not in data:
        return jsonify({'error': 'Faltan datos obligatorios.'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password_hash, data['clave']):
        access_token = create_access_token(identity=user.email)
        logger.info(f'Usuario autenticado: {user.username}')
        return jsonify(access_token=access_token), 200
    logger.warning(f'Credenciales incorrectas para: {data["email"]}')
    return jsonify({'error': 'Credenciales incorrectas.'}), 401

@app.route('/auth/reset_password', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'El correo electrónico es obligatorio.'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        # Aquí iría la lógica para enviar el correo de restablecimiento
        logger.info(f'Solicitud de restablecimiento de contraseña para: {email}')
        return jsonify({'mensaje': 'Solicitud de restablecimiento enviada.'}), 200
    logger.warning(f'Correo no encontrado para restablecimiento: {email}')
    return jsonify({'error': 'Correo no encontrado.'}), 404

@app.route('/auth/reset_password/<string:token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()
    new_password = data.get('new_password')

    if new_password is None:
        return jsonify({'error': 'La nueva contraseña es obligatoria.'}), 400

    try:
        decoded_token = decode_token(token)
        user_email = decoded_token['sub']
        user = User.query.filter_by(email=user_email).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            logger.info(f'Contraseña restablecida para: {user.username}')
            return jsonify({'mensaje': 'Contraseña restablecida exitosamente.'}), 200
    except ExpiredSignatureError:
        logger.warning('Token de restablecimiento expirado.')
        return jsonify({'error': 'El token ha expirado.'}), 400
    except InvalidTokenError:
        logger.warning('Token de restablecimiento inválido.')
        return jsonify({'error': 'Token inválido.'}), 401

@app.route('/usuarios/verificar_y_eliminar', methods=['DELETE'])
def verify_and_delete_user_by_email():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'El correo electrónico es obligatorio.'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        logger.info(f'Usuario verificado y eliminado: {user.username}')
        return jsonify({'mensaje': 'Usuario eliminado exitosamente.'}), 200
    logger.warning(f'Usuario no encontrado para verificar y eliminar: {email}')
    return jsonify({'error': 'Usuario no encontrado.'}), 404

import time

def connect_to_rabbitmq(retries=5, delay=5):
    for attempt in range(retries):
        try:
            credentials = pika.PlainCredentials('user', 'password')
            parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            return channel
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f'Error al conectar con RabbitMQ: {e}. Intento {attempt + 1} de {retries}')
            time.sleep(delay)
    return None

channel = connect_to_rabbitmq()
if channel:
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
    logger.info(" [x] Sent 'Hello World!'")
else:
    logger.error("No se pudo establecer la conexión con RabbitMQ")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)