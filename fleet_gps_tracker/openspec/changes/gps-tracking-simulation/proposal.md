## Why

The `fleet_gps_tracker` module needs a working prototype of vehicle GPS tracking before any real GPS hardware/telemetry feed is available. Stakeholders need to validate the data model and the Google Maps visualization (vehicles, icons, route playback) using simulated coordinate data, so the tracking UX can be reviewed and iterated on early.

## What Changes

- New Odoo 19 module scaffold for `fleet_gps_tracker` (models, views, wizards, security, static assets, manifest).
- New model to represent a tracked vehicle: name, type (car, truck, bicycle, pet) with a distinguishing icon, and current latitude/longitude.
- New model to store recorded/simulated coordinate points: vehicle, datetime, latitude, longitude.
- New "Simular datos" wizard: given a vehicle, a date, and a duration (max 30 minutes), generates a series of simulated coordinate points along a randomized route and stores them.
- New "Generar recorrido" (play) wizard/action: given a start datetime and end datetime, fetches the stored coordinate points in that range and plays them back as an animated route.
- New Google Maps view (OWL component) that renders vehicle markers with type-specific icons and animates the selected route/playback.
- New configuration parameter for the Google Maps JavaScript API key, set via Settings.
- Access rights (`ir.model.access.csv`) for the new models.

## Capabilities

### New Capabilities
- `gps-vehicle-management`: Defines and manages tracked vehicles — name, type/icon (car, truck, bicycle, pet), and current position.
- `gps-coordinate-tracking`: Stores timestamped latitude/longitude points ("recorrido") linked to a vehicle.
- `gps-data-simulation`: Wizard that generates simulated coordinate points for a vehicle given a date and a duration capped at 30 minutes.
- `gps-route-playback`: Wizard/action that retrieves stored coordinate points between a start and end datetime and prepares them for animated playback.
- `gps-map-visualization`: Embeds the Google Maps JavaScript API to display vehicle markers with distinguishing icons and animate route playback.

### Modified Capabilities
- None — this is a new module with no pre-existing specs.

## Impact

- New files under `fleet_gps_tracker/`: `models/`, `wizards/`, `views/`, `security/`, `static/src/`, `data/`, `__manifest__.py`.
- External dependency: Google Maps JavaScript API (requires an API key, stored as a system configuration parameter). No real GPS/telemetry integration yet — coordinates are simulated only.
- New security groups/ACLs for the vehicle and coordinate models.
- No existing specs or code are modified (greenfield module).
