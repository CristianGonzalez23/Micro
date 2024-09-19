Feature: Crear usuario
  Como un administrador
  Quiero poder crear un nuevo usuario
  Para poder gestionar los usuarios en la aplicación

  Scenario Outline: Crear un nuevo usuario
    Given I have user data with name "<nombre>", email "<email>", and password "<clave>"
    When I send a POST request to "/usuarios" with the user data
    Then the response status code should be <status_code>
    And the response body should contain the user ID

    Examples:
      | nombre    | email               | clave     | status_code |
      | Juan      | juan@example.com    | password1 | 201          |
      | Ana       | ana@example.com     | password2 | 201          |
      | Invali | invalidemail.com  | password3 | 400          |
