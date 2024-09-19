Feature: Modificación de información del usuario

  Scenario: Modificar información del usuario
    Given el usuario "user@example.com" inicia sesión con la contraseña "password"
    When el usuario modifica su información con el nuevo nombre "Nuevo Nombre", el nuevo correo "nuevo_email@example.com" y la nueva contraseña "nueva_contraseña"
    Then la respuesta debe ser 200
