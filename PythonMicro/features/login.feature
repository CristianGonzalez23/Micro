Feature: Login de usuario
  Scenario: Usuario inicia sesión con credenciales válidas
    Given I have user data with name "Test User", email "user@example.com", and password "password"
    When I send a POST request to "/auth/login" with the user data
    Then the response status code should be 200
    And the response body should contain the token

  Scenario: Usuario intenta iniciar sesión con credenciales inválidas
    Given I have user data with name "Test User", email "user@example.com", and password "wrongpassword"
    When I send a POST request to "/auth/login" with the user data
    Then the response status code should be 401
