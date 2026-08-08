## ADDED Requirements

### Requirement: Coordinate Point Storage
The system SHALL store coordinate points ("recorrido") with a required vehicle reference, a required recorded datetime, and required latitude and longitude values.

#### Scenario: Store a coordinate point
- **WHEN** a coordinate point is created with a vehicle, a datetime, latitude, and longitude
- **THEN** the system persists the point linked to that vehicle

#### Scenario: Reject a coordinate point without a vehicle
- **WHEN** a coordinate point is created without a vehicle reference
- **THEN** the system rejects the record

### Requirement: Chronological Retrieval Per Vehicle
The system SHALL allow retrieving a vehicle's coordinate points ordered chronologically by recorded datetime, optionally filtered to a datetime range.

#### Scenario: Retrieve points in a date range
- **WHEN** a caller requests a vehicle's coordinate points between a start and end datetime
- **THEN** the system returns only the points within that range, ordered from earliest to latest
