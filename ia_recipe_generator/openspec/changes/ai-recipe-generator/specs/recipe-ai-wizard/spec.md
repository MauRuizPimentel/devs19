## ADDED Requirements

### Requirement: Recipe generation wizard
The system SHALL provide a wizard that lets the user enter a food name or description and, upon confirmation, request a generated recipe from the configured Google AI (Gemini) API.

#### Scenario: Successful generation
- **WHEN** the user opens the wizard, enters "frijoles" as the food name, and clicks confirm
- **THEN** the wizard SHALL call the Google AI API with that description and create a new `recipe.recipe` record populated from the AI response, then display it

### Requirement: Empty food name validation
The system SHALL require the food name field to be non-empty before allowing confirmation.

#### Scenario: Empty input blocked
- **WHEN** the user clicks confirm with an empty food name field
- **THEN** the system SHALL prevent the API call and show a validation error

### Requirement: Missing API key handling
The system SHALL prevent wizard confirmation and show a clear error when no Google AI API key is configured.

#### Scenario: Missing API key
- **WHEN** the user clicks confirm without an API key configured in Settings
- **THEN** the system SHALL raise a user error instructing the user to configure the API key in Settings

### Requirement: AI request failure handling
The system SHALL surface a clear, actionable error to the user when the AI API call fails (timeout, invalid key, quota exceeded, malformed response) and SHALL NOT create a partial recipe record in that case. The raised error message SHALL include the specific error type or code reported by the Gemini API (or, when the API returns no response at all, the underlying exception/network error type), not just a generic failure message.

#### Scenario: AI API returns an error response
- **WHEN** the Google AI API responds with an error (e.g. HTTP 429 quota exceeded, HTTP 401 invalid key, HTTP 400 invalid request)
- **THEN** the wizard SHALL raise a `UserError` whose message includes the HTTP status and the API's reported error code/reason, and SHALL NOT create a `recipe.recipe` record

#### Scenario: AI API call fails before a response is received
- **WHEN** the request to the Google AI API times out or fails at the network level (no HTTP response)
- **THEN** the wizard SHALL raise a `UserError` whose message includes the underlying exception type (e.g. timeout, connection error), and SHALL NOT create a `recipe.recipe` record

#### Scenario: AI API returns malformed data
- **WHEN** the Google AI API responds successfully but the response body does not match the expected recipe schema
- **THEN** the wizard SHALL raise a `UserError` identifying it as a malformed/unexpected response, and SHALL NOT create a `recipe.recipe` record
