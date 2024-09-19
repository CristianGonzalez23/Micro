from behave import given, when, then
import requests

# Este paso se puede reutilizar si ya está en un archivo común como `common_steps.py`
@given('el usuario "{email}" inicia sesión con la contraseña "{clave}" para eliminar un usuario')
def step_impl(context, email, clave):
    context.user_data = {
        'email': email,
        'clave': clave
    }
    response = requests.post('http://localhost:5000/auth/login', json=context.user_data)
    context.response = response
    assert context.response.status_code == 200, 'Error al iniciar sesión'
    context.jwt_token = context.response.json()['token']  # Guardar el token

@when('el usuario elimina el usuario con ID "{user_id}"')
def step_impl(context, user_id):
    headers = {
        'Authorization': f'Bearer {context.jwt_token}'
    }
    response = requests.delete(f'http://localhost:5000/usuarios/{user_id}', headers=headers)
    context.response = response

@then('la respuesta debe ser 204')
def step_impl(context):
    assert context.response.status_code == 204, f'Expected 204, but got {context.response.status_code}'
