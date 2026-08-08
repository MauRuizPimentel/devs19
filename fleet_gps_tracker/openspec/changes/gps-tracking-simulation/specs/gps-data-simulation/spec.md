## ADDED Requirements

### Requirement: Simulate Data Wizard
The system SHALL provide a "Simular datos" action that opens a wizard requesting a vehicle, a date, and a duration in minutes, and generates simulated coordinate points for that vehicle over that window when confirmed.

#### Scenario: Generate simulated points for a vehicle
- **WHEN** a user opens "Simular datos", selects a vehicle, a date, and a duration of 15 minutes, and confirms
- **THEN** the system generates and stores a series of coordinate points for that vehicle timestamped within that 15-minute window starting at the given date

### Requirement: Duration Limit
The system SHALL reject a simulation duration greater than 30 minutes or less than or equal to 0 minutes.

#### Scenario: Reject a duration over 30 minutes
- **WHEN** a user requests a simulation duration of 45 minutes
- **THEN** the system rejects the request and requires a duration between 1 and 30 minutes

#### Scenario: Accept the maximum allowed duration
- **WHEN** a user requests a simulation duration of exactly 30 minutes
- **THEN** the system accepts the request and generates points spanning that window

### Requirement: Plausible Simulated Route
Simulated coordinate points for a single run SHALL form a continuous route, where each point is a small offset from the previous point rather than an unrelated random location.

#### Scenario: Consecutive points stay close together
- **WHEN** a simulation run generates multiple coordinate points
- **THEN** each point's distance from the immediately preceding point is small and bounded, so the sequence traces a continuous path
