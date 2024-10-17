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
import time
import socket
from logging.handlers import SocketHandler

app = Flask(__name__)
app.config.from_object(Config)

# JWT configuration
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Change this to a more secure key
jwt = JWTManager(app)

db.init_app(app)

# Logging configuration
logger = logging.getLogger('python-logger')
logger.setLevel(logging.INFO)

logstash_handler = SocketHandler('logstash', 5044)
logstash_handler.setFormatter(LogstashFormatterV1())

logger.addHandler(logstash_handler)

# Swagger documentation route
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "User API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# RabbitMQ connection
rabbitmq_channel = None

def connect_to_rabbitmq(retries=5, delay=5):
    global rabbitmq_channel
    if rabbitmq_channel is None:
        for attempt in range(retries):
            try:
                credentials = pika.PlainCredentials('user', 'password')
                parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
                connection = pika.BlockingConnection(parameters)
                rabbitmq_channel = connection.channel()
                rabbitmq_channel.queue_declare(queue='hello')
                logger.info("RabbitMQ connection established.")
                return rabbitmq_channel
            except pika.exceptions.AMQPConnectionError as e:
                logger.error(f'Error connecting to RabbitMQ: {e}. Attempt {attempt + 1} of {retries}')
                time.sleep(delay)
    return rabbitmq_channel

def send_to_rabbitmq(message):
    channel = connect_to_rabbitmq()
    if channel:
        channel.basic_publish(exchange='', routing_key='hello', body=message)
        logger.info(f"[x] Sent to RabbitMQ: {message}")

# Function to create a new user
def create_user(username, email, password_hash):
    new_user = User(username=username, email=email, password_hash=password_hash)
    try:
        db.session.add(new_user)
        db.session.commit()
        logger.info(f'User created: {username}')
        send_to_rabbitmq(f"User created: {username}, Email: {email}")
        return {"id": new_user.id, "name": new_user.username, "email": new_user.email}, 201
    except IntegrityError as e:
        db.session.rollback()
        if 'unique constraint' in str(e.orig):
            return {"error": "User already exists."}, 400
        return {"error": "Error creating user."}, 500
    finally:
        db.session.close()

@app.route('/usuarios/', methods=['POST'])
def register_user():
    data = request.get_json()
    if 'nombre' not in data or 'email' not in data or 'clave' not in data:
        return jsonify({'error': 'Missing required data.'}), 400

    password_hash = generate_password_hash(data['clave'])
    result, status_code = create_user(data['nombre'], data['email'], password_hash)
    
    send_to_rabbitmq(f"User registered: {data['nombre']}, Email: {data['email']}")
    
    return jsonify(result), status_code

@app.route('/usuarios/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.get(id)
    if user:
        logger.info(f'User retrieved: {user.username}')
        send_to_rabbitmq(f"User retrieved: {user.username}, ID: {user.id}")
        return jsonify({
            'id': user.id,
            'nombre': user.username,
            'email': user.email,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        })
    logger.warning(f'User not found: ID {id}')
    return jsonify({'error': 'User not found'}), 404

@app.route('/usuarios/actualizar', methods=['PUT'])
@jwt_required()
def update_user():
    current_user_email = get_jwt_identity()
    data = request.get_json()
    email_to_update = data.get('email')

    if current_user_email != email_to_update:
        return jsonify({'error': 'Not authorized to update this user.'}), 403

    user = User.query.filter_by(email=email_to_update).first()
    if user:
        user.username = data.get('nombre', user.username)
        user.email = data.get('email', user.email)
        db.session.commit()
        logger.info(f'User updated: {user.username}')
        send_to_rabbitmq(f"User updated: {user.username}, Email: {user.email}")
        return jsonify({
            'id': user.id,
            'nombre': user.username,
            'email': user.email,
            'updated_at': user.updated_at
        })
    logger.warning(f'User not found for update: {email_to_update}')
    return jsonify({'error': 'User not found'}), 404

@app.route('/usuarios/eliminar', methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user_email = get_jwt_identity()
    data = request.get_json()
    email_to_delete = data.get('email')

    if current_user_email != email_to_delete:
        return jsonify({'error': 'Not authorized to delete this user.'}), 403

    user = User.query.filter_by(email=email_to_delete).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        logger.info(f'User deleted: {user.username}')
        send_to_rabbitmq(f"User deleted: {user.username}, Email: {user.email}")
        return jsonify({'message': 'User successfully deleted.'}), 200
    logger.warning(f'User not found for deletion: {email_to_delete}')
    return jsonify({'error': 'User not found'}), 404

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'email' not in data or 'clave' not in data:
        return jsonify({'error': 'Missing required data.'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password_hash, data['clave']):
        access_token = create_access_token(identity=user.email)
        logger.info(f'User authenticated: {user.username}')
        send_to_rabbitmq(f"User logged in: {user.username}, Email: {user.email}")
        return jsonify(access_token=access_token), 200
    logger.warning(f'Incorrect credentials for: {data["email"]}')
    return jsonify({'error': 'Incorrect credentials.'}), 401

@app.route('/auth/reset_password', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required.'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        # Logic for sending reset email would go here
        logger.info(f'Password reset request for: {email}')
        send_to_rabbitmq(f"Password reset requested: {user.username}, Email: {email}")
        return jsonify({'message': 'Reset request sent.'}), 200
    logger.warning(f'Email not found for reset: {email}')
    return jsonify({'error': 'Email not found.'}), 404

@app.route('/auth/reset_password/<string:token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()
    new_password = data.get('new_password')

    if new_password is None:
        return jsonify({'error': 'New password is required.'}), 400

    try:
        decoded_token = decode_token(token)
        user_email = decoded_token['sub']
        user = User.query.filter_by(email=user_email).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            logger.info(f'Password reset for: {user.username}')
            send_to_rabbitmq(f"Password reset completed: {user.username}, Email: {user_email}")
            return jsonify({'message': 'Password successfully reset.'}), 200
    except ExpiredSignatureError:
        logger.warning('Expired reset token.')
        return jsonify({'error': 'Token has expired.'}), 400
    except InvalidTokenError:
        logger.warning('Invalid reset token.')
        return jsonify({'error': 'Invalid token.'}), 401

@app.route('/usuarios/verificar_y_eliminar', methods=['DELETE'])
def verify_and_delete_user_by_email():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required.'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        logger.info(f'User verified and deleted: {user.username}')
        send_to_rabbitmq(f"User verified and deleted: {user.username}, Email: {email}")
        return jsonify({'message': 'User successfully deleted.'}), 200
    logger.warning(f'User not found for verification and deletion: {email}')
    return jsonify({'error': 'User not found.'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)