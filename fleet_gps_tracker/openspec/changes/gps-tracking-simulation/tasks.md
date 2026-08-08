## 1. Module Scaffold

- [x] 1.1 Create `__manifest__.py` (name, version for Odoo 19, category, depends on `base`/`web`, data/views/security files list, assets bundle)
- [x] 1.2 Create `__init__.py` files for the root module, `models/`, and `wizards/`

## 2. Data Models

- [x] 2.1 Create `models/gps_vehicle.py`: `gps.vehicle` with `name` (required), `vehicle_type` (Selection: car/truck/bicycle/pet, required), `latitude`/`longitude` computed from the latest `gps.coordinate`
- [x] 2.2 Create `models/gps_coordinate.py`: `gps.coordinate` with `vehicle_id` (Many2one, required), `recorded_at` (Datetime, required), `latitude`/`longitude` (Float, required)
- [x] 2.3 Add `_order` on `gps.coordinate` for chronological retrieval and a helper method to fetch a vehicle's points within a datetime range
- [x] 2.4 Register both models in `models/__init__.py`

## 3. Security

- [x] 3.1 Create `security/ir.model.access.csv` with access rights for `gps.vehicle`, `gps.coordinate`, and the two wizard models

## 4. Simulation Wizard ("Simular datos")

- [x] 4.1 Create `wizards/gps_simulate_wizard.py`: TransientModel with `vehicle_id`, `date`, `duration_minutes` fields
- [x] 4.2 Add a `@api.constrains` (or field constraint) rejecting `duration_minutes` outside 1–30
- [x] 4.3 Implement the random-walk generation algorithm: one point every 30 seconds starting from the vehicle's last known position (or a seed point if none), each point offset by a small bounded random delta from the previous one
- [x] 4.4 Implement the confirm action that writes the generated points to `gps.coordinate` with `recorded_at` = date + elapsed seconds
- [x] 4.5 Create `wizards/gps_simulate_wizard_views.xml` form view and a "Simular datos" button/action on the `gps.vehicle` form and list views

## 5. Playback Wizard ("Generar recorrido")

- [x] 5.1 Create `wizards/gps_playback_wizard.py`: TransientModel with `vehicle_id`, `date_from`, `date_to` fields
- [x] 5.2 Implement the confirm action: query `gps.coordinate` for the vehicle in the given range ordered chronologically; if empty, notify the user instead of opening the map
- [x] 5.3 Return a client action that opens the map component pre-loaded with the retrieved points for playback
- [x] 5.4 Create `wizards/gps_playback_wizard_views.xml` form view and a "Generar recorrido" button/action on the `gps.vehicle` form and list views

## 6. Google Maps Configuration

- [x] 6.1 Extend `res.config.settings` with a `google_maps_api_key` field backed by `ir.config_parameter` (`fleet_gps_tracker.google_maps_api_key`)
- [x] 6.2 Add the field to the Settings view (`views/res_config_settings_views.xml`)
- [x] 6.3 Expose the configured key to the frontend (e.g. via a controller or session info) so the OWL component can load the Maps JS API

## 7. Map Visualization (OWL Component)

- [x] 7.1 Add per-type marker icon assets under `static/src/img/` (car, truck, bicycle, pet)
- [x] 7.2 Create the map OWL component that dynamically loads the Google Maps JS API using the configured key — implemented as a shared `gps_map_utils.js` loader/icon helper plus three consumer components (`gps_vehicle_map_field`, `gps_map_overview_action`, `gps_route_playback_action`) instead of one monolithic `gps_map.js`, matching design.md's three distinct map surfaces
- [x] 7.3 Implement rendering of vehicle markers with the type-specific icon for all vehicles with a current position
- [x] 7.4 Implement the "missing API key" / "failed to load" inline message state
- [x] 7.5 Implement playback mode: draw a `Polyline` for the received points and animate a marker through them in chronological order
- [x] 7.6 Register the component as a client action and wire it as the target of the playback wizard's confirm action
- [x] 7.7 Add an embedded map widget on the `gps.vehicle` form centered on the vehicle's current position
- [x] 7.8 Add the JS/XML/SCSS files to the `web.assets_backend` bundle in `__manifest__.py`

## 8. Views & Menus

- [x] 8.1 Create `views/gps_vehicle_views.xml` (list, form) showing name, type, current latitude/longitude
- [x] 8.2 Create `views/gps_coordinate_views.xml` (list) for inspecting stored points, filterable by vehicle and date
- [x] 8.3 Create a top-level menu and full-map client action showing all vehicles' current positions
- [x] 8.4 Add all view/menu XML files to `__manifest__.py` data list

## 9. Manual Verification

- [x] 9.1 Install the module in a local Odoo 19 instance and confirm no install errors
- [ ] 9.2 Configure a Google Maps API key in Settings and confirm the map loads
- [ ] 9.3 Create one vehicle of each type and confirm distinct icons render once positioned
- [ ] 9.4 Run "Simular datos" with a 30-minute duration and confirm 60 bounded, continuous points are stored
- [ ] 9.5 Run "Simular datos" with a 45-minute duration and confirm it is rejected
- [ ] 9.6 Run "Generar recorrido" over the simulated range and confirm the route draws and the marker animates through it
- [ ] 9.7 Run "Generar recorrido" over a range with no data and confirm the empty-state message appears

## 10. Post-Implementation Enhancements

- [x] 10.1 Add a stored `icon` field on `gps.vehicle`, computed from `vehicle_type`, and render it in the list/form views via a new `icon_image` widget
- [x] 10.2 Wire the map components (overview, vehicle-form widget, playback) to use the vehicle's `icon` field instead of deriving the icon URL client-side
- [x] 10.3 Add start/end flag icon assets and render them as static markers at the first/last point of a playback route
- [x] 10.4 Add a click handler + shared `InfoWindow` on vehicle markers (overview map and vehicle-form widget) showing name, latitude/longitude, and last-recorded date
- [ ] 10.5 Manually verify in the browser: vehicle icon shows in list/form, map markers show per-vehicle icons, clicking a marker shows the info window, and playback shows distinct start/end icons
