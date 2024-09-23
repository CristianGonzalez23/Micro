Feature: Restablecimiento de contraseña de usuario

  Scenario: Restablecer la contraseña de un usuario existente
    Given un usuario con el correo "admin@example.com" existe
    When el usuario solicita restablecer la contraseña para "admin@example.com"
    Then el sistema envía un enlace de restablecimiento al correo "admin@example.com"

  Scenario: Crear un usuario nuevo y restablecer la contraseña
    Given el correo "nuevo_usuario@example.com" no existe en el sistema
    When el usuario solicita restablecer la contraseña para "nuevo_usuario@example.com"
    Then el sistema crea un nuevo usuario con el correo "nuevo_usuario@example.com"
    And el sistema envía un enlace de restablecimiento al correo "nuevo_usuario@example.com"
