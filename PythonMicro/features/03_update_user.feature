Feature: Modificación de información del usuario

  Scenario: Modificar información del usuario
    Given el usuario "ana@example.com" inicia sesión con la contraseña "password2" para modificar un usuario
    When el usuario modifica la información con el nuevo nombre "Nuevo Nombre", el nuevo correo "nuevo_email@example.com", la nueva contraseña "nueva_contraseña" para el usuario con ID "4"
    Then la respuesta debe ser 200
