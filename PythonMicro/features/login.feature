Feature: Login de usuario
  Como un administrador
  Quiero poder gestionar el inicio de sesión de los usuarios
  Para asegurarme de que solo los usuarios válidos puedan acceder a la aplicación

  Scenario: Usuario inicia sesión con credenciales válidas
    Given I have user data with name user "test", email "test@gmail.com", and password "12345678"
    When I send a POST request to "/usuarios" with user data
    And I send a POST request to "/auth/login" with user data
    Then the response status code should be 200
    And the response body should contain the JWT token

  Scenario: Usuario intenta iniciar sesión con credenciales inválidas
    Given I have user data with email "test@gmail.com" and password "wrongpassword"
    When I send a POST request to "/auth/login" with user data
    Then the response status code should be 401
