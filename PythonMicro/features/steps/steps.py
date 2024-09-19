import json
from behave import given, when, then
import requests

# Variable global para almacenar los datos del usuario
user_data = {}

@given('I have user data with name "{nombre}", email "{email}", and password "{clave}"')
def step_given_user_data(context, nombre, email, clave):
    context.user_data = {
        'nombre': nombre,
        'email': email,
        'clave': clave
    }

@when('I check if the user exists and delete if necessary')
def step_when_check_and_delete_user(context):
    delete_url = f'http://localhost:5000/usuarios/verificar_y_eliminar'
    response = requests.delete(delete_url, json={'email': context.user_data['email']})

    if response.status_code == 404:
        print('User does not exist, nothing to delete.')
    elif response.status_code not in (200, 204):
        assert False, 'No se pudo eliminar el usuario existente.'

    print(f'Response status code: {response.status_code}')  # Debugging line

@when('I send a POST request to "{endpoint}" with the user data')
def step_when_send_post_request(context, endpoint):
    url = f'http://localhost:5000{endpoint}'
    print(f'Sending request to {url} with data: {context.user_data}')  # Debugging line
    response = requests.post(url, json=context.user_data)
    print(f'Response status code: {response.status_code}')  # Debugging line
    print(f'Response body: {response.text}')  # Debugging line
    context.response = response


@then('the response status code should be {status_code:d}')
def step_then_check_status_code(context, status_code):
    assert context.response.status_code == status_code, f'Expected {status_code}, but got {context.response.status_code}'

@then('the response body should contain the user ID')
def step_then_check_user_id(context):
    response_data = context.response.json()
    assert 'id' in response_data, 'User ID is not in the response'
