from behave import given, when, then
from flask import Flask
import requests

# Suponemos que tu API corre en http://localhost:5000

API_URL = "http://localhost:5000"

@given('un usuario con el correo "{email}" existe')
def step_impl(context, email):
    # Verificamos si el usuario existe llamando a la API
    response = requests.get(f"{API_URL}/usuarios/?email={email}")
    if response.status_code == 404:
        # Si no existe, creamos el usuario
        data = {
            "nombre": "Usuario de prueba",
            "email": email,
            "clave": "test1234"
        }
        requests.post(f"{API_URL}/usuarios/", json=data)

@given('el correo "{email}" no existe en el sistema')
def step_impl(context, email):
    # Verificamos si el usuario existe y lo eliminamos si es necesario
    response = requests.get(f"{API_URL}/usuarios/?email={email}")
    if response.status_code == 200:
        requests.delete(f"{API_URL}/usuarios/verificar_y_eliminar", json={"email": email})

@when('el usuario solicita restablecer la contraseña para "{email}"')
def step_impl(context, email):
    # Simulamos la solicitud de restablecimiento de contraseña
    context.response = requests.post(f"{API_URL}/auth/reset_password", json={"email": email})

@then('el sistema envía un enlace de restablecimiento al correo "{email}"')
def step_impl(context, email):
    assert context.response.status_code == 200, f"Fallo al enviar enlace a {email}"

@then('el sistema crea un nuevo usuario con el correo "{email}"')
def step_impl(context, email):
    response = requests.get(f"{API_URL}/usuarios/?email={email}")
    assert response.status_code == 200, f"El usuario {email} no fue creado correctamente"
