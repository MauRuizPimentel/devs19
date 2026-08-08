## 1. Module scaffold

- [x] 1.1 Create the `ia_recipe_generator` addon skeleton (`__init__.py`, `__manifest__.py` with `depends = ['base', 'web']` and external dependency `requests`)
- [x] 1.2 Create `models/`, `wizard/`, `views/`, `security/`, and `static/src/` directories with their `__init__.py` files (no `data/` directory — this change ships no data XML)

## 2. Recipe model

- [x] 2.1 Implement `recipe.recipe` model (`name`, `instructions`, `preparation_time`, `difficulty`, `image`) in `models/recipe.py`
- [x] 2.2 Add `@api.constrains` validation rejecting a negative `preparation_time`
- [x] 2.3 Add `security/ir.model.access.csv` granting internal users read/create/write access to `recipe.recipe`
- [x] 2.4 Create the `recipe.recipe` list view showing `name`, `preparation_time`, `difficulty`
- [x] 2.5 Add the Recipes menu item and window action for the list view
- [x] 2.6 Bundle a default recipe image (`models/default_recipe_image.py`, a generated PNG icon) and set it as `image`'s `default=` so new recipes always have a stored image; the wizard only overrides it when Gemini's image generation actually returns data

## 3. Google AI (Gemini) client

- [x] 3.1 Implement a Gemini client helper (`models/gemini_client.py`) that reads the API key from `ir.config_parameter` (`ia_recipe_generator.gemini_api_key`) and raises `UserError` when it's missing
- [x] 3.2 Implement the structured `generateContent` request (JSON response schema for `name`, `instructions`, `preparation_time`, `difficulty`) with a request timeout
- [x] 3.3 Validate the parsed JSON response against expected keys/types, raising `UserError` on any mismatch or request failure
- [x] 3.3.1 On HTTP error responses, include the HTTP status and the API's own error code/reason in the raised `UserError` message
- [x] 3.3.2 On network-level failures (timeout, connection error), include the underlying exception's type/name in the raised `UserError` message
- [x] 3.3.3 On a response that doesn't match the expected schema, raise a `UserError` explicitly identifying it as a malformed/unexpected response
- [x] 3.4 Implement the best-effort image generation call, catching all failures and leaving `image` empty on failure

## 4. Recipe generation wizard

- [x] 4.1 Implement `recipe.generate.wizard` (TransientModel) with a required `food_name` field in `wizard/recipe_generate_wizard.py`
- [x] 4.2 Implement the confirm action: validate `food_name` is non-empty, call the Gemini client, create the `recipe.recipe` record, and return a window action showing it
- [x] 4.3 Create the wizard form view (food name input, Confirm/Cancel buttons) as a `target="new"` action
- [x] 4.4 Add a menu item/button to launch the wizard from the Recipes menu
- [x] 4.5 Add `security/ir.model.access.csv` entries for the wizard model

## 5. AI provider settings

- [x] 5.1 Extend `res.config.settings` with `gemini_api_key` (`password="True"`, `config_parameter="ia_recipe_generator.gemini_api_key"`)
- [x] 5.2 Add the settings view section, wrapped in `groups="base.group_system"`, under a new or existing Settings app section
- [x] 5.3 Extend `res.config.settings` with a `gemini_model` Selection field (`config_parameter="ia_recipe_generator.gemini_model"`, choices from `MODEL_CHOICES`) plus a `gemini_model_custom` Char field shown only when "Custom..." is picked, so the model can be changed without a code deploy when Google retires one

## 6. Recipe preview widget

- [x] 6.1 Create the OWL preview dialog component (image, name, preparation time, difficulty) under `static/src/`
- [x] 6.2 Add `static/src/scss/recipe_preview_widget.scss` with the recipe-card styling (image banner, title, time/difficulty badges)
- [x] 6.3 Bundle a placeholder image asset for recipes without a generated image
- [x] 6.4 Implement the "Preview" button as a custom list-view field widget that opens the dialog with the row's data
- [x] 6.5 Register the widget and its assets in `__manifest__.py` (`web.assets_backend`)
- [x] 6.6 Wire the "Preview" button widget into the `recipe.recipe` list view
- [x] 6.7 Show preparation instructions in the preview popup (fetched `invisible="1"` in the list view, rendered via `markup()` + `t-out` since it's rich text) so the popup covers all recipe fields, not just image/name/time/difficulty
- [x] 6.8 Restyle the popup with corporate placeholder tokens (navy/gold) matching the new default recipe image

## 7. Verification

- [x] 7.1 Verified syntax: `py_compile` on all Python files, XML well-formedness on all views/templates, and `node --check` on the OWL widget — all pass. **Not run**: an actual Odoo 19 install, since no live Odoo instance/database is available in this environment.
- [ ] 7.2 Configure a Gemini API key in Settings and generate a recipe end-to-end via the wizard
- [ ] 7.3 Verify the missing-API-key and AI-failure error paths show a clear `UserError` and create no recipe record
- [ ] 7.4 Verify the list view displays name/preparation time/difficulty and the Preview button opens the styled popup, including the placeholder-image fallback
