from behave import given, when, then
import requests

@given('el usuario "{email}" inicia sesión con la contraseña "{clave}"')
def step_impl(context, email, clave):
    context.user_data = {
        'email': email,
        'clave': clave
    }
    response = requests.post('http://localhost:5000/auth/login', json=context.user_data)
    context.response = response
    assert context.response.status_code == 200, 'Login failed'
    context.jwt_token = context.response.json()['token']  # Guardar el token

@when('el usuario modifica su información con el nuevo nombre "{new_name}", el nuevo correo "{new_email}" y la nueva contraseña "{new_password}"')
def step_impl(context, new_name, new_email, new_password):
    headers = {
        'Authorization': f'Bearer {context.jwt_token}'
    }
    user_id = 1  # Cambia esto por el ID del usuario que deseas modificar
    response = requests.put(
        f'http://localhost:5000/usuarios/{user_id}',
        json={"nombre": new_name, "email": new_email, "clave": new_password},
        headers=headers
    )
    context.response = response

@then('la respuesta debe ser 200')
def step_impl(context):
    assert context.response.status_code == 200, f'Expected 200, but got {context.response.status_code}'

@when('the user modifies their information with the new name "{new_name}" and the new email "{new_email}"')
def step_impl(context, new_name, new_email):
    headers = {
        'Authorization': f'Bearer {context.jwt_token}'
    }
    user_id = 1  # Cambia esto por el ID del usuario que deseas modificar
    response = requests.put(
        f'http://localhost:5000/usuarios/{user_id}',
        json={"nombre": new_name, "email": new_email, "clave": context.user_data['clave']},
        headers=headers
    )
    context.response = response
