## ADDED Requirements

### Requirement: Generate Recorrido (Playback) Wizard
The system SHALL provide a "Generar recorrido" action that opens a wizard requesting a vehicle, a start datetime, and an end datetime, and retrieves that vehicle's stored coordinate points within that range when confirmed.

#### Scenario: Retrieve points for playback
- **WHEN** a user opens "Generar recorrido", selects a vehicle, a start datetime, and an end datetime that has stored points
- **THEN** the system retrieves the vehicle's coordinate points within that range, ordered chronologically, and prepares them for playback

#### Scenario: No points in the selected range
- **WHEN** a user requests playback for a vehicle and range with no stored coordinate points
- **THEN** the system informs the user that no route data exists for that range instead of opening an empty map

### Requirement: Animated Route Playback
The system SHALL render the retrieved route as a line on the map, mark its start and end points with distinct icons, and animate a marker moving through the retrieved points in chronological order.

#### Scenario: Route animates on the map
- **WHEN** a playback request returns a sequence of coordinate points
- **THEN** the map draws the full route as a line, places a start icon at the first point and an end icon at the last point, and animates the vehicle's marker moving through each point in order
