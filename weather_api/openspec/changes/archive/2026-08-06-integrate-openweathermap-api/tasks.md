## 1. Module Scaffolding

- [x] 1.1 Create `__manifest__.py` declaring the module, dependency on `base`, and data/security files to load
- [x] 1.2 Create top-level `__init__.py` importing `models` and `wizards`
- [x] 1.3 Create `models/__init__.py` and `wizards/__init__.py`

## 2. API Key Configuration

- [x] 2.1 Extend `res.config.settings` with an `openweathermap_api_key` field backed by `ir.config_parameter` (`weather_api.openweathermap_api_key`)
- [x] 2.2 Add the settings view XML (inherit `res.config.settings` form, add field under a new "Weather API" section) — first install attempt failed with `ParseError: <xpath expr="//div[hasclass('settings')]"> cannot be located in parent view` (that target doesn't exist on Odoo 19's base view); fixed using the modern `<app>/<block>/<setting>` structure inheriting `base.res_config_settings_view_form` at `//form` (see design.md)
- [x] 2.3 Add a helper on the config model or a shared util to read the key and raise a `UserError` with a clear message if it's unset

## 3. Weather Lookup Wizard (backend)

- [x] 3.1 Create `wizards/weather_lookup_wizard.py` with `TransientModel` `weather.lookup.wizard`: input field `city_name` (Char, required) and an invisible technical field `result_json` (Char, JSON-encoded result)
- [x] 3.2 Implement `action_fetch_weather()`: read the API key (via 2.3), call `GET https://api.openweathermap.org/data/2.5/weather` with `q=city_name`, `units=metric`, `appid=<key>`, timeout=10s
- [x] 3.3 Handle response: on success, build a JSON payload with `resolved_location`, `country_code`, `temperature`, `condition_main`, `condition_description`, write it to `result_json`, and return an `ir.actions.act_window` reopening the same wizard so the dialog refreshes and the footer widget renders (returning nothing relied on implicit dialog reload, which didn't visibly update anything in testing); any HTTP 4xx is treated as one client-error branch (surfacing the status + OpenWeatherMap's own `message`, never the API key) rather than hardcoding 401/404 separately, and HTTP 5xx/network errors as "service temporarily unavailable"
- [x] 3.4 Ensure no code path logs or displays the raw API key
- [x] 3.5 Create the wizard form view: `city_name` input in the body, `<footer>` containing the "Fetch Weather"/"Close" buttons plus `<field name="result_json" widget="weather_result" invisible="not result_json"/>`
- [x] 3.6 Create the window action and menu item to open the wizard

## 4. Weather Result Widget (frontend)

- [x] 4.1 Create `static/src/js/weather_result_widget.js`: OWL component parsing `result_json` (via `willUpdateProps`/`setup`), computing the flag emoji from `country_code`, and mapping `condition_main` to a FontAwesome icon class (per design.md table, with fallback for unmapped values); register it in the `fields` registry as `weather_result`
- [x] 4.2 Create `static/src/xml/weather_result_widget.xml`: OWL template rendering the flag, the temperature as a large number, and the condition icon
- [x] 4.3 Create `static/src/scss/weather_result_widget.scss`: corporate-styled layout (flag/temperature/icon row or card), using SCSS variables for colors/spacing isolated at the top of the file for easy rebranding
- [x] 4.4 Register all three files under `assets: {'web.assets_backend': [...]}` in `__manifest__.py`
- [x] 4.5 Confirm the FontAwesome version bundled with the target Odoo 19 install includes the icon classes chosen in design.md; adjust fallbacks if any class is missing — confirmed FA 4.7; `fa-cloud-rain`/`fa-smog` don't exist, replaced with `fa-tint`/`fa-cloud`

## 5. Security

- [x] 5.1 Add `security/ir.model.access.csv` granting internal users (`base.group_user`) read/write/create access to `weather.lookup.wizard`
- [x] 5.2 Verify the settings field is only visible/editable by users with `base.group_system` (standard Settings behavior — confirm no override needed) — no group override was added on the field/view, so it inherits the standard Settings-screen access restriction to `base.group_system`

## 6. Verification

- [ ] 6.1 Manually test: configure a valid API key, look up a known city, confirm the footer widget shows the correct flag, large temperature, and matching condition icon
- [ ] 6.2 Manually test: look up an invalid/unknown city, confirm a clear error is shown and no widget appears
- [ ] 6.3 Manually test: clear the API key, attempt a lookup, confirm the configuration error message appears and no widget is shown
- [ ] 6.4 Manually test: confirm a user without access to the wizard's action cannot open it
- [ ] 6.5 Manually test: verify widget styling matches corporate visual guidelines (colors, spacing, typography) once brand tokens are confirmed (see design.md Open Questions)
- [x] 6.6 Confirm no API key value appears in any error message, view, or log output at `info` level or above — verified by code inspection: `api_key` is only used as an outbound request parameter, never passed to `_logger` or `UserError`
