Feature: Eliminación de un usuario

  Scenario: Eliminar un usuario
    Given el usuario "ana@example.com" inicia sesión con la contraseña "password2" para eliminar un usuario
    When el usuario elimina el usuario con ID "2"
    Then la respuesta debe ser 204
