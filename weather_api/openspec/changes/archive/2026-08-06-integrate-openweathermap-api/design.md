## Context

`weather_api` is currently an empty Odoo 19 module. This change introduces its first functionality: an on-demand lookup against the OpenWeatherMap Current Weather Data API. There is no existing HTTP-client pattern, credential storage, or wizard code in this module to build on, so the foundational choices are made here.

## Goals / Non-Goals

**Goals:**
- Let a user fetch current weather for a city name from within Odoo, on demand.
- Store the OpenWeatherMap API key safely and make it easy for an administrator to configure.
- Fail clearly and safely when the key is missing/invalid or the API is unreachable.

**Non-Goals:**
- No historical storage of weather data (no persistent `weather.record` model).
- No scheduled/cron polling of weather data.
- No linking weather data to other Odoo models (`res.partner`, addresses, etc.) — out of scope for this change.
- No support for providers other than OpenWeatherMap.

## Decisions

**Wizard model, not a persistent model.**
The lookup is modeled as a `TransientModel` wizard (`weather.lookup.wizard`) rather than a regular `Model`. Results are request-scoped and don't need to survive beyond the session. Alternative considered: a persistent `weather.query` model to keep a query log — rejected because the proposal explicitly excludes historical persistence, and it would add ACL/data-retention surface area with no current requirement driving it.

**API key stored as an `ir.config_parameter`, exposed via `res.config.settings`.**
Odoo's system parameters are the standard place for module-level configuration that isn't per-user. Exposing it through a `res.config.settings` field (rather than a raw settings-menu record) gives administrators the familiar Settings UI and keeps the field's visibility governed by the existing `base_setup` access rules (settings screens are already admin-only). Alternative considered: a dedicated `weather.config` model — rejected as unnecessary indirection for a single credential.

Odoo 17+ replaced the old `div.settings`/`o_setting_box` inheritance target with a declarative `<app>`/`<block>`/`<setting>` structure. A first install attempt inheriting `base.res_config_settings_view_form` with `<xpath expr="//div[hasclass('settings')]">` failed with `ParseError: cannot be located in parent view`, confirmed against a real Odoo 19 example in this repo (`enterprise/databases/views/res_config_settings_views.xml`). Fixed by inheriting `base.res_config_settings_view_form`, targeting `//form` with `position="inside"`, and wrapping the field in `<app name="weather_api" groups="base.group_system"><block><setting>...</setting></block></app>` — the same pattern that module uses to add a new standalone settings tab.

**HTTP calls via Python `requests`, called synchronously from the wizard action.**
Odoo already depends on `requests`; no new external library is needed. Calls happen synchronously when the user submits the wizard, with an explicit timeout (10s) — there's no background job because the use case is a single on-demand lookup, not a batch operation.

**Error handling maps to `UserError`.**
Network errors, non-200 responses, and "city not found" responses are all caught and re-raised as `odoo.exceptions.UserError` with a user-safe message. The raw API key and raw response body are never included in the message or logged at a level visible to non-admins; technical details go to `_logger.warning` at most, keyed by request context, not by dumping the key.

**City name geocoding delegated to the OpenWeatherMap endpoint itself.**
The `weather` endpoint (`/data/2.5/weather?q=<city>`) accepts a city name directly, so no separate geocoding step or coordinate lookup is needed for the initial scope.

**Result rendered by a dedicated OWL component, not plain form fields.**
A `WeatherResultWidget` OWL component renders the result: country flag, large temperature, and condition icon. Its three concerns are split into separate files, following this repo's existing convention of grouping by file type rather than by component (matching sibling modules in `addons/19/addons/`):
- `static/src/js/weather_result_widget.js` — component class + registration as a custom field widget in the `fields` registry
- `static/src/xml/weather_result_widget.xml` — OWL `<templates>` markup
- `static/src/scss/weather_result_widget.scss` — corporate styling
All three are declared together in `__manifest__.py` under `assets: { 'web.assets_backend': [...] }`. Alternative considered: a single inline-template OWL component defined entirely in the `.js` file — rejected per the explicit requirement to keep JS/XML/SCSS separate, and because separate files are the prevailing convention in Odoo's own addons for anything beyond a one-line template.

**Widget is a custom field widget bound to a technical `result_json` field, embedded in the wizard's `<footer>`.**
The wizard gets an invisible `result_json` (`fields.Char`, JSON-encoded) field populated by `action_fetch_weather()`. The view places `<field name="result_json" widget="weather_result" invisible="not result_json"/>` inside `<footer>`, alongside the action buttons. `action_fetch_weather()` explicitly returns an `ir.actions.act_window` reopening the same wizard `res_id` with `target: "new"` — relying on the button call implicitly reloading the dialog (returning nothing) was tried first and produced no visible update at all in real testing, so the explicit reopen is what's implemented. The component then parses the JSON in `setup()`/`willUpdateProps()` from the refreshed field value. Alternative considered: opening a second wizard/dialog to show results — rejected because the requirement is explicit about showing the widget in the *same* wizard's footer after accepting.

**Country flag rendered via Unicode regional-indicator emoji derived from the API's ISO country code**, not a bundled flag-image library.
OpenWeatherMap's response includes `sys.country` (ISO 3166-1 alpha-2, e.g. `"US"`, `"CO"`). The component converts that code to its flag emoji (each letter maps to a Unicode regional indicator symbol) and renders it at large size via SCSS — zero additional static assets, no image licensing/attribution to manage. Alternative considered: bundling a flag sprite/icon library (e.g., `flag-icons`) for pixel-perfect vector flags — deferred; revisit if emoji flag rendering proves visually inconsistent across the organization's supported browsers/OS fonts.

**Weather condition icon mapped from OpenWeatherMap's `weather[0].main` category to existing FontAwesome classes already bundled with Odoo's web assets** (no new icon assets). Confirmed against `enterprise/web/static/src/libs/fontawesome/css/font-awesome.css`: Odoo 19 bundles **FontAwesome 4.7**, which lacks the FA5-only `fa-cloud-rain` and `fa-smog` icons — the mapping uses FA4-available equivalents instead:
| `main` value | icon class |
|---|---|
| `Clear` | `fa-sun-o` |
| `Clouds` | `fa-cloud` |
| `Rain`, `Drizzle` | `fa-tint` |
| `Thunderstorm` | `fa-bolt` |
| `Snow` | `fa-snowflake-o` |
| `Mist`, `Fog`, `Haze`, `Smoke` | `fa-cloud` |
| *(unmapped/other)* | `fa-question-circle-o` |

**Corporate styling is isolated in the component's SCSS file, using SCSS variables for color/spacing** rather than hard-coded hex values inline, so the actual brand palette can be dropped in without touching JS/XML. The specific corporate color tokens (primary color, font, spacing scale) are not yet defined in this repo and are called out as an open question below.

## Risks / Trade-offs

- **[Risk]** OpenWeatherMap free-tier rate limits (60 calls/minute) could be hit under heavy manual use → **Mitigation**: synchronous on-demand design naturally limits call volume to human-driven usage; document the limit in the module description; revisit if usage patterns change.
- **[Risk]** API key stored in `ir.config_parameter` is visible to any code with `sudo()` access within the Odoo instance → **Mitigation**: this is the standard Odoo pattern for this class of secret (same as many OCA connector modules); mark the parameter as not exported in `ir.config_parameter` export/import if that becomes relevant.
- **[Risk]** Ambiguous city names (e.g., "Springfield") may return an unexpected location → **Mitigation**: display the resolved location name (including country code) returned by the API alongside the results, so the user can immediately verify OpenWeatherMap matched what they intended.
- **[Trade-off]** No caching of results means repeated lookups for the same city re-call the API → acceptable given the low expected call volume of an on-demand, human-triggered feature; can be revisited later without a spec change since it's an implementation detail.
- **[Risk]** Flag emoji rendering depends on OS/browser font support for regional-indicator sequences (inconsistent on some older Windows/Linux configurations) → **Mitigation**: this is a known, documented limitation of the emoji-flag approach; if the organization's supported browser matrix has poor coverage, switch to a bundled flag-icon library (see Decisions) as a follow-up.
- **[Risk]** "Corporate styles" are not yet defined in this repo (no existing brand SCSS tokens found in this module) → **Mitigation**: SCSS variables are isolated in one file (see Decisions) so real brand values can be swapped in without touching component logic; see Open Questions.

## Migration Plan

Net-new module functionality; no data migration. Deploying is a normal module upgrade (`-u weather_api`). Rollback is a straightforward downgrade/uninstall since no other module depends on this functionality yet.

## Open Questions

- Should the wizard support units (metric vs. imperial) as a user-facing toggle, or default to metric only for this first iteration? Defaulting to metric (°C, m/s) for now; can be added as a follow-up change if needed.
- What are the actual corporate brand tokens (primary/secondary colors, typography, spacing scale) to use in `weather_result_widget.scss`? None were found elsewhere in this module/repo. Implementation should reuse the company's existing Odoo theme variables if any exist company-wide (e.g., `res.company` report colors or a shared corporate SCSS partial); otherwise this needs a value from whoever owns the brand guidelines before the SCSS is finalized.
- Is emoji-rendered flag acceptable for the target audience's devices, or should a vector flag-icon library be used from the start?
