Feature: Modificación de información del usuario


  Scenario: User logs in with valid credentials
    Given I have user data with name user "andres", email "andres@gmail.com", password "12345678"
    When I check if the users exists and delete
    And I send a POST request to "/usuarios" with user
    Then the response status code should 201

  Scenario: modify user information
    Given the user "andres@gmail.com" logs in with the password "12345678" to modify a user
    When the user modifies the information with the new name "New Name" and the new email "new_email@example.com"
    Then the response should be 200