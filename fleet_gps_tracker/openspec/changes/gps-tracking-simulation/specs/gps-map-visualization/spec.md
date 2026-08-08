## ADDED Requirements

### Requirement: Google Maps API Key Configuration
The system SHALL allow an administrator to configure a Google Maps JavaScript API key via Settings, and SHALL use that key to load the map.

#### Scenario: Configure the API key
- **WHEN** an administrator sets the Google Maps API key in Settings and saves
- **THEN** the map view uses that key when loading the Google Maps JavaScript API

#### Scenario: Missing API key
- **WHEN** a user opens a map view and no Google Maps API key is configured
- **THEN** the system shows a message indicating the API key is missing instead of an empty or broken map

### Requirement: Vehicle Markers On The Map
The map SHALL display a marker for each vehicle that has a current position, using the icon that corresponds to its type.

#### Scenario: Multiple vehicles shown with distinct icons
- **WHEN** the map loads with a car, a truck, a bicycle, and a pet, each having a current position
- **THEN** the map shows four markers, each using the icon for its respective type

#### Scenario: Vehicles without a position are omitted
- **WHEN** a vehicle has no recorded coordinate points
- **THEN** the map does not display a marker for that vehicle

### Requirement: Vehicle Info On Click
The map SHALL show the vehicle's name, current coordinates, and last-recorded date when its marker is clicked.

#### Scenario: Click a vehicle marker
- **WHEN** a user clicks a vehicle's marker on the map
- **THEN** the map shows an info window with that vehicle's name, latitude/longitude, and the date/time it was last recorded
