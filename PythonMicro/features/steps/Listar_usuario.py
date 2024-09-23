import requests
from behave import given, when, then
import json

@given('el administrador ha iniciado sesión con email "{email}" y clave "{clave}"')
def step_given_admin_login(context, email, clave):
    context.user_data = {
        'email': email,
        'clave': clave
    }
    
    # Intentar iniciar sesión
    response = requests.post('http://localhost:5000/auth/login', json=context.user_data)
    print(f"Login response: {response.status_code}")
    print(f"Login response content: {response.text}")
    
    # Si el usuario no existe, crearlo
    if response.status_code != 200:
        print("User does not exist. Creating new user.")
        create_user_response = requests.post('http://localhost:5000/usuarios', json={
            'nombre': 'Administrador',
            'email': email,
            'clave': clave
        })
        print(f"Create user response: {create_user_response.status_code}")
        print(f"Create user response content: {create_user_response.text}")
        assert create_user_response.status_code == 201, f'Error al crear usuario: {create_user_response.status_code}'
        
        # Intentar iniciar sesión nuevamente
        response = requests.post('http://localhost:5000/auth/login', json=context.user_data)
        print(f"Second login attempt response: {response.status_code}")
        print(f"Second login attempt content: {response.text}")
    
    context.response = response
    assert response.status_code == 200, f'Error al iniciar sesión: {response.status_code}'
    
    # Guardar el token JWT para las próximas solicitudes
    context.jwt_token = response.json()['token']
    print(f"JWT Token obtained: {context.jwt_token[:10]}...")

@when('el administrador solicita la lista de usuarios desde el endpoint "{endpoint}"')
def step_when_admin_requests_users(context, endpoint):
    headers = {
        'Authorization': f'Bearer {context.jwt_token}'
    }
    # Solicitar la lista de usuarios
    url = f'http://localhost:5000{endpoint}'
    print(f"Requesting users from: {url}")
    response = requests.get(url, headers=headers)
    print(f"Get users response: {response.status_code}")
    print(f"Get users response content: {response.text}")
    context.response = response

@then('la respuesta debe tener un status code {status_code:d}')
def step_then_check_status_code(context, status_code):
    assert context.response.status_code == status_code, f'Expected {status_code}, but got {context.response.status_code}'

@then('la respuesta debe contener la lista de usuarios')
def step_then_check_users_list(context):
    try:
        response_data = context.response.json()
    except json.JSONDecodeError:
        print(f"Failed to decode JSON. Response content: {context.response.text}")
        raise

    # Verificar que la lista de usuarios esté presente
    assert 'users' in response_data, f'No se encontró la lista de usuarios en la respuesta. Contenido: {response_data}'
    assert len(response_data['users']) > 0, 'La lista de usuarios está vacía'
    
    # Imprimir la lista de usuarios
    print("Lista de usuarios:")
    for user in response_data['users']:
        print(f"- ID: {user.get('id')}, Nombre: {user.get('nombre')}, Email: {user.get('email')}")


@then('la lista de usuarios debe incluir "{email}"')
def step_then_list_includes_user(context, email):
    response_data = context.response.json()
    assert 'users' in response_data, 'No se encontró la lista de usuarios en la respuesta'
    user_emails = [user['email'] for user in response_data['users']]
    assert email in user_emails, f'El email {email} no se encontró en la lista de usuarios'
    print(f"El usuario {email} está presente en la lista de usuarios.")

@when('un usuario no autenticado solicita la lista de usuarios desde el endpoint "{endpoint}"')
def step_when_unauthenticated_user_requests(context, endpoint):
    url = f'http://localhost:5000{endpoint}'
    print(f"Requesting users without authentication from: {url}")
    response = requests.get(url)
    print(f"Unauthenticated get users response: {response.status_code}")
    print(f"Unauthenticated get users response content: {response.text}")
    context.response = response

@then('cada usuario en la lista debe tener un id, nombre y email')
def step_then_check_user_data_structure(context):
    response_data = context.response.json()
    assert 'users' in response_data, 'No se encontró la lista de usuarios en la respuesta'
    for user in response_data['users']:
        assert 'id' in user, f'Usuario sin ID: {user}'
        assert 'nombre' in user, f'Usuario sin nombre: {user}'
        assert 'email' in user, f'Usuario sin email: {user}'
    print("Todos los usuarios tienen id, nombre y email.")