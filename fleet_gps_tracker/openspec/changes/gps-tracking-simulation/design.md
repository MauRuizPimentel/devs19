## Context

`fleet_gps_tracker` is a brand-new Odoo 19 module (no existing code, no existing specs). There is no real GPS/telemetry feed yet, so the module must stand on simulated data while still exercising the real data model and the real Google Maps visualization that will later receive live coordinates. The module must not depend on Odoo's built-in `fleet` app — vehicle types include non-fleet entities (bicycle, pet), so a self-contained model is more appropriate than extending `fleet.vehicle`.

## Goals / Non-Goals

**Goals:**
- Store vehicles with a distinguishing type/icon (car, truck, bicycle, pet) and their current position.
- Store a time-series of coordinate points ("recorrido") per vehicle.
- Let a user generate simulated coordinate points for a vehicle over a bounded window (date + duration ≤ 30 minutes).
- Let a user play back stored points between a start and end datetime as an animated route on a Google Map.
- Render vehicles and playback routes using the Google Maps JavaScript API, with per-type icons.

**Non-Goals:**
- Real GPS/telemetry hardware or device integration (future phase).
- Road-network-accurate routing/snapping (Directions API, traffic-aware routing).
- Historical analytics/reporting beyond raw point storage.
- Multi-company/security rule design beyond standard ACLs.
- Simultaneous multi-vehicle playback (single vehicle per playback run in this phase).

## Decisions

### 1. Two dedicated models, not an extension of `fleet.vehicle`
`gps.vehicle` (name, `vehicle_type` selection: car/truck/bicycle/pet, current `latitude`/`longitude`) and `gps.coordinate` (`vehicle_id` many2one, `recorded_at` datetime, `latitude`, `longitude`).
- **Alternative considered**: extend Odoo's `fleet.vehicle`. Rejected — it pulls in the full Fleet app (drivers, contracts, odometer, etc.) and its vocabulary doesn't fit bicycles/pets, which are core to this prototype.

### 2. Icon is derived from `vehicle_type`, not stored per record
The map component maps `vehicle_type` → a bundled icon (`static/src/img/`) client-side. No icon upload field in this phase.
- **Alternative considered**: a `Binary` icon upload field per vehicle. Rejected as unnecessary complexity for a fixed, small set of types.

### 3. Simulation is a random-walk wizard, not teleportation between two points
`gps.simulate.wizard` (TransientModel): `vehicle_id`, `date`, `duration_minutes` (constrained `1–30`). Starting from the vehicle's last known position (or a default seed point if none exists), it generates one point every 30 seconds (≤ 60 points per run), each a small random offset from the previous point, and writes them to `gps.coordinate` with `recorded_at` = date + elapsed seconds. This keeps the simulated route visually plausible (a wandering path) instead of a straight jump.
- **Alternative considered**: interpolate a straight line between two random endpoints. Rejected — looks unrealistic on the map and doesn't exercise multi-point playback well.

### 4. Playback is a server-side range query + client-side animation
`gps.playback.wizard` (TransientModel): `vehicle_id`, `date_from`, `date_to` (Datetime). On confirm, it queries `gps.coordinate` for that vehicle ordered by `recorded_at` in the range and opens a client action passing the point list. The OWL map component draws a `google.maps.Polyline` for the full route and animates a marker through the points on a timer.
- **Alternative considered**: animate server-side and push updates via bus. Rejected as unnecessary — the point set for a ≤30-minute simulation is small enough to send to the client in one payload and animate locally.

### 5. Google Maps JS API key stored as a system parameter, loaded dynamically
The key is stored in `ir.config_parameter` (`fleet_gps_tracker.google_maps_api_key`), editable via a `res.config.settings` field. The OWL map component injects the Google Maps JS `<script>` loader at runtime using that key; if unset, the component shows an inline message instead of a blank/broken map.
- **Alternative considered**: hardcode the key in module data. Rejected — API keys are environment-specific and must be configurable/rotatable without code changes.

### 6. Map surfaces
A dedicated menu/client action shows the full map with all vehicles' current positions; the vehicle form has an embedded map widget centered on that vehicle's current position. Playback opens the same map component in a modal/client action, focused on the selected vehicle's route.

## Risks / Trade-offs

- **[Risk]** Google Maps JS API requires a billing-enabled key; without one the map silently fails. → **Mitigation**: explicit config field + inline error message when the key is missing or the script fails to load; document key setup (enable "Maps JavaScript API", restrict by HTTP referrer) in the module README.
- **[Risk]** Random-walk simulation can place points anywhere (ocean, no road network) since there's no map-snapping. → **Mitigation**: acceptable for this prototype phase; documented as a known limitation, not a defect.
- **[Risk]** The Maps JS API key is necessarily exposed to the browser. → **Mitigation**: this is expected Google Maps JS usage; mitigated operationally via HTTP-referrer key restriction in Google Cloud Console, not in code.
- **[Risk]** Unbounded simulation runs could flood `gps.coordinate`. → **Mitigation**: hard constraint of ≤30 minutes and a fixed 30-second sampling interval caps each run at 60 rows.

## Migration Plan

New module, first install — no migration from prior state.
1. Install `fleet_gps_tracker`.
2. Set the Google Maps API key in Settings.
3. Create one or more `gps.vehicle` records.
4. Run "Simular datos" to populate `gps.coordinate`.
5. Run "Generar recorrido" to play back the simulated route.

Rollback: uninstalling the module removes its models/data; no impact on other modules since it has no external Odoo module dependencies beyond `base`/`web`.

## Open Questions

- Should "Simular datos" eventually support generating data for multiple vehicles in one run, or stay single-vehicle? (Current scope: single-vehicle.)
- Should playback eventually support viewing multiple vehicles' routes on the same map simultaneously? (Current scope: single-vehicle.)
