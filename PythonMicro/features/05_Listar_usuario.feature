Feature: Gestión y listado de usuarios
  Como administrador del sistema,
  Quiero poder gestionar usuarios y obtener una lista de ellos,
  Para poder administrar efectivamente el sistema.

  Scenario: Obtener la lista de usuarios con un administrador existente
    Given el administrador ha iniciado sesión con email "admin@example.com" y clave "admin123"
    When el administrador solicita la lista de usuarios desde el endpoint "/usuarios/"
    Then la respuesta debe tener un status code 200
    And la respuesta debe contener la lista de usuarios

  Scenario: Crear nuevo administrador y listar usuarios
    Given el administrador ha iniciado sesión con email "nuevo_admin@example.com" y clave "nueva_clave123"
    When el administrador solicita la lista de usuarios desde el endpoint "/usuarios/"
    Then la respuesta debe tener un status code 200
    And la respuesta debe contener la lista de usuarios
    And la lista de usuarios debe incluir "nuevo_admin@example.com"

  Scenario: Intentar listar usuarios sin autenticación
    When un usuario no autenticado solicita la lista de usuarios desde el endpoint "/usuarios/"
    Then la respuesta debe tener un status code 401

  Scenario: Verificar la estructura de los datos de usuario
    Given el administrador ha iniciado sesión con email "admin@example.com" y clave "admin123"
    When el administrador solicita la lista de usuarios desde el endpoint "/usuarios/"
    Then la respuesta debe tener un status code 200
    And cada usuario en la lista debe tener un id, nombre y email

  Scenario Outline: Listar usuarios con diferentes administradores
    Given el administrador ha iniciado sesión con email "<email>" y clave "<clave>"
    When el administrador solicita la lista de usuarios desde el endpoint "/usuarios/"
    Then la respuesta debe tener un status code 200
    And la respuesta debe contener la lista de usuarios

    Examples:
      | email                | clave       |
      | admin1@example.com   | admin1pass  |
      | admin2@example.com   | admin2pass  |
      | admin3@example.com   | admin3pass  |