from flask import Flask, jsonify, request
from config import Config
from models import db, User
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    decode_token,
    verify_jwt_in_request
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
import smtplib
from logging.handlers import SocketHandler
from email.mime.text import MIMEText
from flask_cors import CORS  # Importar flask-cors
from flask_migrate import Migrate  # Importar Flask-Migrate

app = Flask(__name__)
app.config.from_object(Config)

# Habilitar CORS
CORS(app)

# JWT configuration
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Cambia esto a una clave más segura
jwt = JWTManager(app)

db.init_app(app)
migrate = Migrate(app, db)  # Configurar Flask-Migrate


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
    global rabbitmq_channel
    try:
        if rabbitmq_channel is None or rabbitmq_channel.is_closed:
            rabbitmq_channel = connect_to_rabbitmq()
        rabbitmq_channel.basic_publish(exchange='', routing_key='hello', body=message)
        logger.info(f"[x] Sent to RabbitMQ: {message}")
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Failed to send message to RabbitMQ: {e}")
        rabbitmq_channel = None  # Reset the channel to force reconnection

# Email notification function
def send_email_notification(to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = 'cristianr.gonzalezi@uqvirtual.edu.co'
        msg['To'] = to_email

        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        from_email = "cristianr.gonzalezi@uqvirtual.edu.co"
        password = "Crisgonza_20"

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())

        logger.info(f'Email sent to: {to_email}')
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")

# Function to create a new user
def create_user(data):
    new_user = User(
        username=data['nombre'],
        email=data['email'],
        password_hash=generate_password_hash(data['clave']),
        personal_page=data.get('personal_page'),
        nickname=data.get('nickname'),
        contact_public=data.get('contact_public', False),
        address=data.get('address'),
        biography=data.get('biography'),
        organization=data.get('organization'),
        country=data.get('country'),
        social_links=data.get('social_links')
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        logger.info(f'User created: {new_user.username}')
        
        # Send RabbitMQ message
        send_to_rabbitmq(f"User created: {new_user.username}, Email: {new_user.email} ")
        
        # Send email notification
        send_email_notification(
            to_email=new_user.email,
            subject="Bienvenido a la plataforma",
            body=f"Hola {new_user.username}, tu usuario ha sido creado con éxito."
        )

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
    required_fields = ['nombre', 'email', 'clave']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required data.'}), 400

    result, status_code = create_user(data)
    
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
            'personal_page': user.personal_page,
            'nickname': user.nickname,
            'contact_public': user.contact_public,
            'address': user.address,
            'biography': user.biography,
            'organization': user.organization,
            'country': user.country,
            'social_links': user.social_links,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        })
    logger.warning(f'User not found: ID {id}')
    return jsonify({'error': 'User not found'}), 404

@app.route('/usuarios/', methods=['GET'])
@jwt_required()
def list_users():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    users = User.query.paginate(page=page, per_page=limit, error_out=False)
    total = users.total
    users_list = [{
        'id': user.id,
        'nombre': user.username,
        'email': user.email,
        'personal_page': user.personal_page,
        'nickname': user.nickname,
        'contact_public': user.contact_public,
        'address': user.address,
        'biography': user.biography,
        'organization': user.organization,
        'country': user.country,
        'social_links': user.social_links,
        'created_at': user.created_at,
        'updated_at': user.updated_at
    } for user in users.items]
    
    logger.info(f'Users listed: Page {page}, Limit {limit}')
    send_to_rabbitmq(f"Users listed: Page {page}, Limit {limit}")
    
    return jsonify({
        'total': total,
        'page': page,
        'limit': limit,
        'users': users_list
    }), 200

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
        user.personal_page = data.get('personal_page', user.personal_page)
        user.nickname = data.get('nickname', user.nickname)
        user.contact_public = data.get('contact_public', user.contact_public)
        user.address = data.get('address', user.address)
        user.biography = data.get('biography', user.biography)
        user.organization = data.get('organization', user.organization)
        user.country = data.get('country', user.country)
        user.social_links = data.get('social_links', user.social_links)
        db.session.commit()
        logger.info(f'User updated: {user.username}')
        
        # Send email notification
        send_email_notification(
            to_email=email_to_update,
            subject="Actualización de perfil",
            body=f"Hola {user.username}, tu perfil ha sido actualizado."
        )
        
        send_to_rabbitmq(f"User updated: {user.username}, Email: {user.email}")
        return jsonify({
            'id': user.id,
            'nombre': user.username,
            'email': user.email,
            'personal_page': user.personal_page,
            'nickname': user.nickname,
            'contact_public': user.contact_public,
            'address': user.address,
            'biography': user.biography,
            'organization': user.organization,
            'country': user.country,
            'social_links': user.social_links,
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
        
        # Send email notification
        send_email_notification(
            to_email=email_to_delete,
            subject="Cuenta eliminada",
            body=f"Hola {user.username}, tu cuenta ha sido eliminada."
        )
        
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
        # Incluir el correo electrónico en el token
        access_token = create_access_token(identity={'email': user.email})
        logger.info(f'User authenticated: {user.username}')
        
        # Enviar notificación por correo electrónico con el token en el cuerpo
        send_email_notification(
            to_email=user.email,
            subject="Inicio de sesión",
            body=f"Hola {user.username}, has iniciado sesión exitosamente.\n\nTu token de acceso es: **{access_token}**"
        )
        
        send_to_rabbitmq(f"User logged in: {user.username}, Email: {user.email}")
        return jsonify({'token': access_token}), 200
    return jsonify({'error': 'Invalid credentials.'}), 401

@app.route('/auth/reset_password', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    if 'email' not in data:
        return jsonify({'error': 'Missing required data.'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user:
        reset_token = create_access_token(identity=user.email, expires_delta=timedelta(hours=1))
        reset_link = f"http://localhost:5000/auth/reset_password/{reset_token}"
        
        send_email_notification(
            to_email=user.email,
            subject="Restablecimiento de contraseña",
            body=f"Hola {user.username}, usa el siguiente enlace para restablecer tu contraseña: {reset_link}"
        )
        
        logger.info(f'Password reset requested for: {user.username}')
        send_to_rabbitmq(f"Password reset requested for: {user.username}, Email: {user.email}")
        
        return jsonify({'message': 'Password reset link sent to your email.'}), 200
    return jsonify({'error': 'User not found.'}), 404

@app.route('/auth/reset_password/<token>', methods=['POST'])
def reset_password(token):
    try:
        decoded_token = decode_token(token)
        email = decoded_token['sub']
    except (ExpiredSignatureError, InvalidTokenError):
        return jsonify({'error': 'Invalid or expired token.'}), 401

    data = request.get_json()
    if 'clave' not in data:
        return jsonify({'error': 'Missing required data.'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        user.password_hash = generate_password_hash(data['clave'])
        db.session.commit()
        
        logger.info(f'Password reset for: {user.username}')
        send_to_rabbitmq(f"Password reset for: {user.username}, Email: {user.email}")
        
        return jsonify({'message': 'Password reset successfully.'}), 200
    return jsonify({'error': 'User not found.'}), 404

# Endpoint para Prometheus /metrics en formato de texto
@app.route('/metrics', methods=['GET'])
def metrics():
    # Ejemplo de métrica básica que se puede monitorear

    metrics_text = f"# HELP notifications_count Número de notificaciones\n# TYPE notifications_count gauge\n "
    return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/verify_token', methods=['POST'])
def verify_token():
    data = request.get_json()
    token = data.get('token')

    try:
        decoded_token = decode_token(token)
        return jsonify({'valid': True}), 200
    except (ExpiredSignatureError, InvalidTokenError):
        return jsonify({'valid': False}), 401





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)