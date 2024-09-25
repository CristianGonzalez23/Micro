Feature: Listar usuarios

  Scenario: Listar usuarios después de iniciar sesión
    Given el usuario "juan@example.com" con la contraseña "password1" existe y ha iniciado sesión para listar usuarios
    When el usuario solicita la lista de usuarios
    Then el sistema devuelve la lista de usuarios