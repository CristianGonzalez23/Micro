import json
from behave import given, when, then
import requests

@given('I have user data with email "{email}" and password "{clave}"')
def step_given_user_data(context, email, clave):
    context.user_data = {
        'email': email,
        'clave': clave
    }

@when('the user sends a post request to "{endpoint}" with the user data')
def step_when_send_post_request(context, endpoint):
    
    url = f'http://localhost:5000{endpoint}'  # Asegúrate de que la URL sea correcta
    response = requests.post(url, json=context.user_data)
    context.response = response

@then('the response body should contain the JWT token')
def step_then_check_token(context):
    response_data = context.response.json()
    assert 'token' in response_data, 'JWT token is not in the response'
    context.jwt_token = response_data['token']  # Guardar el token para usarlo más tarde

@then(u'the response body should contain the token')
def step_impl(context):
    # Verifica que la respuesta tenga un cuerpo JSON
    assert context.response is not None, 'No response received'

    # Intenta obtener el token del cuerpo de la respuesta
    response_data = context.response.json()
    assert 'token' in response_data, 'Token not found in the response'

    # Si deseas almacenar el token para su uso posterior, hazlo aquí
    context.jwt_token = response_data['token']

