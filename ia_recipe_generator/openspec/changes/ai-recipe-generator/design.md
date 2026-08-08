## Context

`ia_recipe_generator` is a new, greenfield Odoo 19 addon (no existing models or views to preserve). It needs to call an external service — Google's Generative Language API (Gemini) — to turn a short food name into a structured recipe, then let users browse and preview the results inside Odoo.

## Goals / Non-Goals

**Goals:**
- Let a user type a food name and get back a stored, structured recipe (name, instructions, preparation time, difficulty).
- Show recipes in a simple list and offer a visually polished popup preview (image, name, time, difficulty).
- Keep the Google AI API key configurable and protected, without hardcoding it.

**Non-Goals:**
- Recipe editing/versioning workflows, ratings, categories, or multi-language recipes.
- Support for AI providers other than Google's Gemini API.
- Multi-company/record-rule scoping — recipes are shared across all internal users, same as a simple reference list.
- Guaranteed recipe images — image generation is best-effort; a missing image is an accepted outcome (covered by the placeholder fallback in the widget spec).

## Decisions

### Module & data model
- Module technical name: `ia_recipe_generator`, `depends = ['base', 'web']`, external Python dependency `requests` declared in the manifest.
- `recipe.recipe` (persistent model): `name` (Char, required), `instructions` (Html), `preparation_time` (Integer, minutes, `>= 0` via `@api.constrains`), `difficulty` (Selection: `easy`/`medium`/`hard`, required), `image` (Image/Binary, optional).
  - Alternative considered: store preparation time as a Float duration widget. Rejected — an integer minute count is simpler and matches what the AI naturally returns.

### Wizard & AI call
- `recipe.generate.wizard` (TransientModel): single field `food_name` (Char, required), opened as a `target="new"` action from the Recipes menu.
- Confirm button calls a service method that:
  1. Reads the API key from `ir.config_parameter` (`ia_recipe_generator.gemini_api_key`); raises `UserError` if unset (satisfies the missing-key requirement).
  2. Calls the Gemini `generateContent` REST endpoint with `response_mime_type: application/json` and an explicit `response_schema` (`name`, `instructions`, `preparation_time`, `difficulty`) so the model returns directly-parseable structured data instead of free-form text.
  3. On any request/parse failure, raises a `UserError` whose message names the specific failure: for an HTTP error response, the HTTP status plus the API's own error code/reason (e.g. `HTTP 429 RESOURCE_EXHAUSTED`, `HTTP 401 UNAUTHENTICATED`); for a network-level failure (timeout, connection error), the underlying exception's type/name; for a response that doesn't match the expected schema, an explicit "malformed response" message. No record is created in any of these cases.
  4. On success, creates the `recipe.recipe` record and returns a window action showing it.
  - Alternative considered: prompt-engineer free-text output and parse it with regex. Rejected — Gemini's structured-output mode (JSON schema) is materially more reliable and avoids brittle parsing.
- Image generation is a second, best-effort call to a Gemini image-capable model using the same API key. Failures (quota, model unavailable, no image in response) are caught and simply leave `image` empty — this is not surfaced as an error to the user, since the recipe itself is still valid without a picture.

### Settings
- Extend `res.config.settings` with `gemini_api_key` (Char, `password="True"` widget, `config_parameter="ia_recipe_generator.gemini_api_key"`).
- The settings section is wrapped with `groups="base.group_system"` so only administrators can see or edit it, addressing the access-restriction requirement without a new security group.
- Also extend it with `gemini_model` (Selection, `config_parameter="ia_recipe_generator.gemini_model"`, options from `MODEL_CHOICES`, default `gemini-2.5-flash`) plus a `gemini_model_custom` (Char, `config_parameter="ia_recipe_generator.gemini_model_custom"`) shown only when `gemini_model == "custom"`. Google periodically retires Gemini model IDs (observed firsthand: `gemini-2.0-flash` hit a zero free-tier quota, `gemini-2.5-flash-lite` returned HTTP 404 as "no longer available to new users") on a timeline this change can't track. A dropdown of known-good IDs avoids typos (e.g. pasting the `models/` resource prefix), while the "Custom..." escape hatch keeps the field usable once a newer model outpaces this module's hardcoded list. `GeminiClient._get_text_model()` resolves `custom` to the free-text value, falling back to `DEFAULT_TEXT_MODEL` if either is unset, and strips a stray `models/` prefix regardless of which path was used.
  - Alternative considered: keep it a free-text Char field only. Rejected — a dropdown removes the "wrong format" class of error entirely for the common case; the custom fallback keeps the free-text case available for when the dropdown goes stale.
  - `gemini_model` deliberately does not use the `config_parameter=` auto-binding despite the pattern used elsewhere in this module: Odoo's automatic binding writes/reads the raw `ir.config_parameter` string straight into the Selection field without validating it against the field's choices. A value stored before this field existed as a Selection (e.g. free text typed into the earlier Char version) crashes the settings form on load instead of degrading gracefully. `get_values()`/`set_values()` overrides validate the stored value explicitly, falling back to `"custom"` (carrying the old text into `gemini_model_custom`) when it doesn't match a known choice.
  - Alternative considered: keep it hardcoded and update the constant reactively when it breaks. Rejected after it broke twice in a row during initial testing — the failure mode is entirely predictable and administrator-fixable without a deploy.

### List view & preview widget
- `recipe.recipe` list view shows `name`, `preparation_time`, `difficulty`; `image` and `instructions` are fetched `invisible="1"` so the preview widget has them without adding visible columns.
- A custom OWL field widget (registered on the list view) renders a "Preview" button per row. On click, it opens an OWL `Dialog` (`@web/core/dialog/dialog`) passing the record's image, name, preparation time, difficulty, and instructions as props — no extra server round-trip, since the list already holds that data.
  - Alternative considered: a `type="object"` button calling a server action that returns a `client` action. Rejected — a pure front-end Dialog is faster and simpler for data the list view already has in memory.
- The dialog shows all four recipe fields (image, name, time, difficulty, and the preparation instructions), not just the three originally scoped, per explicit user request that the popup cover "todos los campos". Instructions (an Html field, sanitized server-side by Odoo's default `fields.Html` behavior) are rendered via Owl's `markup()` + `t-out`, not `t-esc`, since it's rich text.
- The dialog's content is a dedicated OWL component with its own SCSS (`static/src/scss/recipe_preview_widget.scss`) styled as a recipe card (image banner, title, time/difficulty badges, instructions section) using placeholder corporate tokens (navy `#14293d` / gold `#c89b3c`) pending real brand values, rather than reusing plain form-field rendering. When `image` is falsy, the component renders a bundled placeholder image — though this should be rare in practice now (see below).
- `recipe.recipe.image` has a `default=` — a small bundled PNG (a flat fork-and-knife icon in the same navy/gold palette, generated once and stored as a base64 constant in `models/default_recipe_image.py`) — so every recipe has a real stored image from creation, not just a UI-only fallback. The wizard only sets `image` explicitly in its `create()` call when Gemini's best-effort image generation actually returns data; when it doesn't, the key is omitted so the model default applies.
  - Alternative considered: keep the bundled image as an SVG (simpler to author/edit). Rejected — Odoo's `fields.Image` processes stored values through Pillow on write, which cannot handle SVG; the default had to be a real raster PNG. The SVG placeholder remains, but only as the OWL widget's own last-resort fallback for pre-existing records saved before this default existed.

## Risks / Trade-offs

- [External API latency/downtime blocks the wizard's confirm action] → enforce a request timeout, disable the confirm button while the call is in flight, and surface a `UserError` on timeout rather than hanging.
- [Gemini API key stored in `ir.config_parameter` is plaintext in the database] → restrict the settings UI to `base.group_system`, use the `password` widget so it isn't shown on screen; document that this is a standard Odoo system parameter, not a secrets vault, so it inherits the DB's existing access controls.
- [Structured-output schema drifts from what the model actually returns] → validate the parsed JSON against expected keys/types before creating the record; treat any mismatch as a generation failure (`UserError`), never a partially-filled recipe.
- [Image generation is unreliable/optional] → treat it as best-effort and never block recipe creation on it; the widget already has a placeholder fallback.

## Migration Plan

Fresh module install — no existing data to migrate. Rollback is a plain module uninstall, which drops the `recipe.recipe` table and the wizard's transient table; the only persisted cross-cutting artifact is the `ia_recipe_generator.gemini_api_key` system parameter, which is harmless to leave behind or remove.

## Open Questions

- Should generated recipes be scoped per-user (owned) or fully shared across all internal users? This design assumes shared, matching a simple company-wide recipe list; revisit if multi-tenant separation is needed later.
- Should there be a manual "regenerate image" action if the best-effort image call fails? Out of scope for this change; can be a follow-up.
