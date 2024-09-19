import json
from behave import given, when, then
import requests
import logging

# Configura el logging al nivel INFO
logging.basicConfig(level=logging.INFO)


# Paso para definir los datos del usuario para crear uno nuevo
@given('I have user data with name user "{nombre}", email "{email}", and password "{clave}"')
def step_given_user_data(context, nombre, email, clave):
    context.user_data = {
        'nombre': nombre,
        'email': email,
        'clave': clave
    }

@when('I check if the users exists and delete if necessary')
def step_when_check_and_delete_user(context):
    delete_url = f'http://localhost:5000/usuarios/verificar_y_eliminar'
    response = requests.delete(delete_url, json={'email': context.user_data['email']})

    if response.status_code == 404:
        print('User does not exist, nothing to delete.')
    elif response.status_code not in (200, 204):
        assert False, 'No se pudo eliminar el usuario existente.'

    print(f'Response status code: {response.status_code}')  # Debugging line

# Paso para definir los datos del usuario para iniciar sesión
@given('I have user data with email "{email}" and password "{clave}"')
def step_given_user_data_with_email(context, email, clave):
    context.user_data = {
        'email': email,
        'clave': clave
    }

# Paso para enviar la solicitud POST
@when('I send a POST request to "{endpoint}" with user data')
def step_when_send_post_request(context, endpoint):
    url = f'http://localhost:5000{endpoint}'  # Asegúrate de que la URL sea correcta
    headers = {'Content-Type': 'application/json'}  # Incluimos los headers manualmente
    response = requests.post(url, json=context.user_data, headers=headers)  # Asegura el formato JSON
    context.response = response

# Paso para verificar el código de estado
@then('the response status code should be {status_code:d}')
def step_then_check_status_code(context, status_code):
    assert context.response.status_code == status_code, f'Expected status code {status_code}, but got {context.response.status_code}'

@then('the response body should contain the JWT token')
def step_then_check_token(context):
    response_data = context.response.json()
    
    # Ajusta la clave según la respuesta de tu API
    token_key = 'token'  # Cambia a 'access_token' si es necesario
    
    assert token_key in response_data, f'JWT token "{token_key}" no está en la respuesta'
    
    context.jwt_token = response_data[token_key]
    
    # Utiliza logging en lugar de print para asegurar que se muestre en la salida de Behave
    import logging
    logging.info(f'Token JWT Generado: {context.jwt_token}')
