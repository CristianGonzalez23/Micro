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

@when('I send a POST request to "{endpoint}" with the user data')
def step_when_send_post_request(context, endpoint):
    url = f'http://localhost:5000{endpoint}'  # Asegúrate de que la URL sea correcta
    response = requests.post(url, json=context.user_data)
    context.response = response

@then('the response status code should be {status_code:d}')
def step_then_check_status_code(context, status_code):
    assert context.response.status_code == status_code, f'Expected {status_code}, but got {context.response.status_code}'

@then('the response body should contain the user ID')
def step_then_check_user_id(context):
    response_data = context.response.json()
    assert 'id' in response_data, 'User ID is not in the response'
