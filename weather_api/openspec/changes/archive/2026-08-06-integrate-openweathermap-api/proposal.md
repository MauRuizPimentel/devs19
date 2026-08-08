## Why

The `weather_api` module currently has no functionality. Users need a way to look up current weather conditions for a location directly from Odoo — for example, to inform field visits, logistics planning, or partner communications — without leaving the ERP or relying on an external tool.

## What Changes

- New on-demand weather lookup: a user enters a location (city name or coordinates) and retrieves current weather conditions (temperature, description, humidity, wind speed) from the OpenWeatherMap Current Weather Data API.
- New configuration for storing the OpenWeatherMap API key as a system parameter, editable from Settings.
- New wizard for entering a location; on accepting the wizard, the result is rendered as a visual widget in the wizard's footer showing: the queried country's flag, the temperature as a large number, and an icon representing the weather condition (sunny, cloudy, rainy, etc.), styled to match corporate branding.
- The result widget is a dedicated OWL component with its JS, XML template, and SCSS split into separate files (standard Odoo asset structure), not inline markup.
- No historical persistence: results are fetched live per request and are not stored as database records.

## Capabilities

### New Capabilities
- `weather-lookup`: On-demand current weather queries against the OpenWeatherMap API, triggered by a user-provided location, returning temperature, conditions, humidity, and wind data.
- `weather-api-configuration`: Secure storage and management of the OpenWeatherMap API key used to authenticate outbound requests.

### Modified Capabilities
(none — this is a new module with no existing specs)

## Impact

- New module code: wizard model, view (form + action), menu item, security/ACL entries, `res.config.settings` extension for the API key.
- New frontend assets: an OWL result widget (JS + XML + SCSS files) registered in `web.assets_backend`.
- New outbound HTTP dependency: calls to `api.openweathermap.org` at request time.
- Requires an OpenWeatherMap API key to be configured before the feature works; no key means the lookup returns a clear configuration error rather than failing silently.
- No changes to existing modules or database schema outside `weather_api`.
