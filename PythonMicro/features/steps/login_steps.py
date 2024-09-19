import json
from behave import given, when, then
import requests

@given('I have user data with name user "{nombre}", email "{email}", and password "{clave}"')
def step_given_user_data(context, nombre, email, clave):
    context.user_data = {
        'nombre': nombre,
        'email': email,
        'clave': clave
    }

@given('I have user data with email "{email}" and password "{clave}"')
def step_given_user_data_with_email(context, email, clave):
    context.user_data = {
        'email': email,
        'clave': clave
    }

@when('I send a POST request to "{endpoint}" with user data')
def step_when_send_post_request(context, endpoint):
    url = f'http://localhost:5000{endpoint}'  # Asegúrate de que la URL sea correcta
    response = requests.post(url, json=context.user_data)
    context.response = response

@then('the response status code should be {status_code:d}')
def step_then_check_status_code(context, status_code):
    assert context.response.status_code == status_code, f'Expected status code {status_code}, but got {context.response.status_code}'

@then('the response body should contain the JWT token')
def step_then_check_token(context):
    response_data = context.response.json()
    
    # Asegúrate de que el token esté en la respuesta
    assert 'token' in response_data, 'JWT token is not in the response'
    
    # Guardar el token en el contexto
    context.jwt_token = response_data['token']
    
    # Imprimir el token en la consola
    print(f'Generated JWT Token: {context.jwt_token}')

