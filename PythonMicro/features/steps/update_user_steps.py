from behave import given, when, then
import requests

# Paso para iniciar sesión antes de modificar un usuario
@given('el usuario "{email}" inicia sesión con la contraseña "{clave}" para modificar un usuario')
def step_impl(context, email, clave):
    context.user_data = {
        'email': email,
        'clave': clave
    }
    response = requests.post('http://localhost:5000/auth/login', json=context.user_data)
    context.response = response
    assert context.response.status_code == 200, 'Error al iniciar sesión'
    context.jwt_token = context.response.json()['token']  # Guardar el token

# Paso para modificar la información de un usuario
@when('el usuario modifica la información con el nuevo nombre "{new_name}", el nuevo correo "{new_email}", la nueva contraseña "{new_password}" para el usuario con ID "{user_id}"')
def step_impl(context, new_name, new_email, new_password, user_id):
    headers = {
        'Authorization': f'Bearer {context.jwt_token}'
    }
    response = requests.put(
        f'http://localhost:5000/usuarios/{user_id}',
        json={"nombre": new_name, "email": new_email, "clave": new_password},
        headers=headers
    )
    context.response = response

# Validar que la respuesta sea 200
@then('la respuesta debe ser 200')
def step_impl(context):
    assert context.response.status_code == 200, f'Expected 200, but got {context.response.status_code}'
