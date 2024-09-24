from behave import given, when, then
import requests


import requests
from behave import given, when, then

# Paso para definir los datos del usuario para crear uno nuevo
@given('I have user data for creation with name user "{nombre}", email "{email}", password "{clave}"')
def step_given_user_data_for_creation(context, nombre, email, clave):
    context.user_data = {
        'nombre': nombre,
        'email': email,
        'clave': clave
    }

@when('I check if the user exists and delete for creation')
def step_when_check_and_delete_user_for_creation(context):
    delete_url = f'http://localhost:5000/usuarios/verificar_y_eliminar'
    response = requests.delete(delete_url, json={'email': context.user_data['email']})

    if response.status_code == 404:
        print('User does not exist, nothing to delete.')
    elif response.status_code not in (200, 204):
        assert False, 'No se pudo eliminar el usuario existente.'

    print(f'Response status code: {response.status_code}')  # Debugging line

# Paso para enviar la solicitud POST
@when('I send a POST request to "{endpoint}" with user for creation')
def step_when_send_post_request_for_creation(context, endpoint):
    url = f'http://localhost:5000{endpoint}'  # Asegúrate de que la URL sea correcta
    headers = {'Content-Type': 'application/json'}  # Incluimos los headers manualmente
    response = requests.post(url, json=context.user_data, headers=headers)  # Asegura el formato JSON
    context.response = response

# Paso para verificar el código de estado
@then('the response status code for creation should be {status_code:d}')
def step_then_check_status_code_for_creation(context, status_code):
    assert context.response.status_code == status_code, f'Expected status code {status_code}, but got {context.response.status_code}'


# Paso para iniciar sesión antes de eliminar un usuario
@given('the user "{email}" logs in with the password "{clave}" to delete a user')
def step_given_user_logs_in_to_delete(context, email, clave):
    context.user_data = {
        'email': email,
        'clave': clave
    }
    response = requests.post('http://localhost:5000/auth/login', json=context.user_data)
    context.response = response
    assert context.response.status_code == 200, 'Error al iniciar sesión'
    context.jwt_token = context.response.json()['token']  # Guardar el token

# Paso para eliminar un usuario
@when('the user delete user for email')
def step_when_user_deletes_account(context):
    headers = {
        'Authorization': f'Bearer {context.jwt_token}'
    }
    response = requests.delete(
        'http://localhost:5000/usuarios/eliminar',
        headers=headers,
        json={'email': context.user_data['email']}
    )
    context.response = response

# Validar que la respuesta sea 204
@then('the response should be 204')
def step_then_response_should_be_204(context):
    assert context.response.status_code == 204, f'Expected 204, but got {context.response.status_code}'