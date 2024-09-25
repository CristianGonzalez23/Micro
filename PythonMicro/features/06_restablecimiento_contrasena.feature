Feature: Restablecimiento de contraseña

  Scenario: Restablecer contraseña para un usuario, creando uno nuevo si no existe
    Given el correo "usuario@example.com" puede no existir en el sistema
    When el usuario solicita restablecer la contraseña para "usuario@example.com"
    Then si el usuario no existe, el sistema lo crea con el correo "usuario@example.com"
    And el sistema envía un enlace de restablecimiento al correo "usuario@example.com"
