## ADDED Requirements

### Requirement: On-demand current weather lookup
The system SHALL allow a user to request current weather conditions for a location by entering a city name, and SHALL display the returned temperature, weather description, humidity, and wind speed.

#### Scenario: Successful lookup by city name
- **WHEN** a user enters a valid city name and submits the lookup
- **THEN** the system calls the OpenWeatherMap Current Weather Data API and displays temperature, weather description, humidity, and wind speed for that city

#### Scenario: OpenWeatherMap rejects the request (city not found, invalid key, or other client error)
- **WHEN** OpenWeatherMap responds with any HTTP 4xx status (e.g. city not found, invalid API key)
- **THEN** the system displays a clear error message including the HTTP status and OpenWeatherMap's own description of the problem, without exposing the API key value or raising an unhandled exception

#### Scenario: API unreachable, times out, or returns a server error
- **WHEN** the OpenWeatherMap API does not respond within the configured timeout, or responds with an HTTP 5xx status
- **THEN** the system displays an error message indicating the weather service is temporarily unavailable

### Requirement: Visual weather result widget
The system SHALL present a successful lookup result as a visual widget — not plain text fields — displaying the queried location's country flag, the temperature as a large prominent number, and an icon representing the weather condition (e.g., sunny, cloudy, rainy, snowy), styled per corporate visual guidelines. The widget SHALL appear in the wizard's footer once the user accepts/confirms the lookup.

#### Scenario: Widget renders after a successful lookup
- **WHEN** a user submits a valid city and the API call succeeds
- **THEN** the wizard footer displays a widget showing the country flag, the temperature as a large number, and an icon matching the returned weather condition

#### Scenario: Widget reflects the correct condition icon
- **WHEN** the API returns a weather condition category (e.g., clear, clouds, rain, snow, thunderstorm)
- **THEN** the widget displays an icon that visually corresponds to that category

#### Scenario: No widget shown before a lookup or on failure
- **WHEN** the wizard is first opened, or a lookup fails (not found, missing key, or unreachable API)
- **THEN** the result widget is not shown; only the corresponding error message (or empty input state) is displayed

### Requirement: Access control for weather lookup
The system SHALL restrict use of the weather lookup wizard to internal users who have been granted access rights to it.

#### Scenario: Authorized user performs a lookup
- **WHEN** an internal user with access to the weather lookup wizard opens it and submits a location
- **THEN** the system processes the request and displays results

#### Scenario: Unauthorized user is denied access
- **WHEN** a user without the required access rights attempts to open the weather lookup action
- **THEN** the system denies access according to standard Odoo access control enforcement
