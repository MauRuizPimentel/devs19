## ADDED Requirements

### Requirement: Vehicle Registration
The system SHALL allow a user to create a vehicle record with a required name and a required type selected from: car, truck, bicycle, pet.

#### Scenario: Create a vehicle with valid data
- **WHEN** a user creates a vehicle with name "Camión 1" and type "truck"
- **THEN** the system saves the vehicle record with that name and type

#### Scenario: Reject a vehicle without a name
- **WHEN** a user attempts to save a vehicle without a name
- **THEN** the system rejects the save and requires a name

### Requirement: Type-Based Icon
The system SHALL expose an `icon` field on each vehicle, derived from its type (car, truck, bicycle, pet), so different vehicle kinds are visually distinguishable both in the backend UI and on the map.

#### Scenario: Icon reflects vehicle type
- **WHEN** a vehicle has type "bicycle"
- **THEN** its `icon` field points to the bicycle icon, distinct from the icons used for car, truck, and pet
- **AND** the map renders that vehicle's marker with the same bicycle icon

### Requirement: Current Position
Each vehicle SHALL expose its current latitude and longitude, reflecting its most recently recorded coordinate point.

#### Scenario: Position updates after simulation
- **WHEN** a new coordinate point is recorded for a vehicle
- **THEN** the vehicle's current latitude and longitude reflect that most recent point

#### Scenario: No position yet
- **WHEN** a vehicle has no coordinate points recorded
- **THEN** the vehicle's current latitude and longitude are empty and the map does not place a marker for it
