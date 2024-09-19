Feature: Autenticación de usuarios
  Como un usuario registrado
  Quiero poder iniciar sesión
  Para acceder a recursos protegidos

Scenario: Usuario inicia sesión con credenciales válidas
    Given I have user data with name user "nini", email "nini@gmail.com", and password "12345678"
    When I send a POST request to "/usuarios" with user data
    Then the response status code should be 200


  Scenario: Iniciar sesión exitosamente con credenciales correctas
    Given I have user data with email "nini@gmail.com" and password "12345678"
    When I send a POST request to "/auth/login" with user data
    Then the response status code should be 200
    And the response body should contain the JWT token
