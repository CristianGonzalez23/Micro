Feature: Eliminación de un usuario

  Scenario: Eliminar un usuario
    Given el usuario "invalidemail.com" inicia sesión con la contraseña "password3" para eliminar un usuario
    When el usuario elimina el usuario con ID "3"
    Then la respuesta debe ser 204
