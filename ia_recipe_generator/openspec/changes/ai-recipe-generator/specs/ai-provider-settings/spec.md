## ADDED Requirements

### Requirement: Google AI API key configuration
The system SHALL provide a Settings section where an administrator can enter and save the Google AI (Gemini) API key.

#### Scenario: Saving the API key
- **WHEN** an administrator enters an API key in Settings and saves
- **THEN** the key SHALL be stored as a protected system parameter usable by the recipe generation wizard

### Requirement: API key protection
The system SHALL restrict access to the stored API key to administrators and SHALL NOT expose it in client-side views, exports, or logs.

#### Scenario: Key not exposed to non-admin users
- **WHEN** a non-administrator user views the application Settings
- **THEN** the API key field SHALL NOT be visible to that user

### Requirement: Access restricted to administrators
The system SHALL restrict who can view or edit the AI settings to users with administration rights.

#### Scenario: Restricted access enforced
- **WHEN** a user without administration rights attempts to open the AI settings section
- **THEN** the system SHALL deny access according to Odoo's security groups
