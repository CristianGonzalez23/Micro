Feature: User management for deletion

@run_this

  Scenario: User logs in with valid credentials
    Given I have user data for creation with name user "fabiana", email "fabiana@gmail.com", password "12345678"
    When I check if the user exists and delete for creation
    And I send a POST request to "/usuarios" with user for creation
    Then the response status code for creation should be 201

  Scenario: delete user information
    Given the user "fabiana@gmail.com" logs in with the password "12345678" to delete a user
    When the user delete user for email
    Then the response should be 204