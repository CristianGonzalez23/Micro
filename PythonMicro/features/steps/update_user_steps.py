from behave import given, when, then
import requests


# Paso para definir los datos del usuario para crear uno nuevo
@given('I have user data with name user "{nombre}", email "{email}", password "{clave}"')
def step_given_user_data(context, nombre, email, clave):
    context.user_data = {
        'nombre': nombre,
        'email': email,
        'clave': clave
    }

@when('I check if the users exists and delete')
def step_when_check_and_delete_user(context):
    delete_url = f'http://localhost:5000/usuarios/verificar_y_eliminar'
    response = requests.delete(delete_url, json={'email': context.user_data['email']})

    if response.status_code == 404:
        print('User does not exist, nothing to delete.')
    elif response.status_code not in (200, 204):
        assert False, 'No se pudo eliminar el usuario existente.'

    print(f'Response status code: {response.status_code}')  # Debugging line

# Paso para enviar la solicitud POST
@when('I send a POST request to "{endpoint}" with user')
def step_when_send_post_request(context, endpoint):
    url = f'http://localhost:5000{endpoint}'  # Asegúrate de que la URL sea correcta
    headers = {'Content-Type': 'application/json'}  # Incluimos los headers manualmente
    response = requests.post(url, json=context.user_data, headers=headers)  # Asegura el formato JSON
    context.response = response

# Paso para verificar el código de estado
@then('the response status code should {status_code:d}')
def step_then_check_status_code(context, status_code):
    assert context.response.status_code == status_code, f'Expected status code {status_code}, but got {context.response.status_code}'



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
