from behave import given, when, then
import requests
from werkzeug.security import generate_password_hash
import allure
import json

API_URL = "http://localhost:5000"

@given('el usuario "{email}" con la contraseña "{clave}" existe y ha iniciado sesión para listar usuarios')
def step_given_user_exists_and_logs_in(context, email, clave):
    # Verificar si el usuario existe
    response = requests.get(f"{API_URL}/usuarios/?email={email}")
    if response.status_code == 404:
        # Crear el usuario si no existe
        data = {
            "nombre": "Juan Pérez",
            "email": email,
            "clave": generate_password_hash(clave)
        }
        create_response = requests.post(f"{API_URL}/usuarios/", json=data)
        assert create_response.status_code == 201, f'Error al crear usuario: {create_response.status_code} - {create_response.text}'
    
    # Iniciar sesión
    login_data = {
        'email': email,
        'clave': clave
    }
    login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
    context.response = login_response
    assert context.response.status_code == 200, f'Error al iniciar sesión: {login_response.status_code} - {login_response.text}'
    context.jwt_token = context.response.json()['token']

@when('el usuario solicita la lista de usuarios')
def step_when_user_requests_user_list(context):
    headers = {'Authorization': f'Bearer {context.jwt_token}'}
    context.response = requests.get(f"{API_URL}/usuarios/", headers=headers)
    assert context.response.status_code == 200, f'Error al solicitar la lista de usuarios: {context.response.status_code} - {context.response.text}'

@then('el sistema devuelve la lista de usuarios')
def step_then_system_returns_user_list(context):
    response_json = context.response.json()
    print(f'Response JSON: {response_json}')  # Imprimir la respuesta JSON para depuración
    assert 'users' in response_json, f'Response does not contain user list: {response_json}'
    
    # Adjuntar la respuesta al reporte de Allure
    allure.attach(
        json.dumps(response_json, indent=2),
        name="Lista de Usuarios",
        attachment_type=allure.attachment_type.JSON
    )
    
    # Imprimir la lista de usuarios en la consola
    users_list = response_json['users']
    for user in users_list:
        print(f"Usuario: {user}")