## Why

Cooks and home users want quick recipe ideas without searching multiple sites: they type a dish name (e.g. "huevos", "frijoles") and expect a ready-to-use recipe. This module adds that capability to Odoo 19 by generating recipes on demand through Google's generative AI (Gemini), turning a one-word idea into a structured recipe record with a polished preview.

## What Changes

- New Odoo 19 addon `ia_recipe_generator`.
- New `recipe.recipe` model to persist generated recipes: name, preparation instructions, preparation time, difficulty level.
- New wizard (`TransientModel`) that asks the user for a food name/description and, on confirm, calls the Google AI (Gemini) API to generate a recipe for that dish and stores it as a `recipe.recipe` record.
- New list view for `recipe.recipe` showing name, preparation time, and difficulty level.
- New "Preview" button on the recipe list that opens a popup (OWL widget/dialog) styled as a recipe card: recipe image, name, preparation time, and difficulty level.
- New Settings section to configure the Google AI (Gemini) API key used by the wizard, stored server-side (not exposed to the browser).

## Capabilities

### New Capabilities
- `recipe-model`: Odoo model and list view storing/displaying generated recipes (name, instructions, preparation time, difficulty).
- `recipe-ai-wizard`: Wizard that collects a food name and calls the Google AI (Gemini) API to generate a recipe, creating a `recipe.recipe` record from the result.
- `recipe-preview-widget`: Button on the recipe list that opens a styled OWL popup showing the recipe's image, name, preparation time, and difficulty.
- `ai-provider-settings`: Configuration screen for storing the Google AI (Gemini) API key used to authenticate generation requests.

### Modified Capabilities
- None (new module, no existing specs affected).

## Impact

- New addon directory (models, wizards, views, security, static/src for the OWL widget, and a settings extension) — no existing code is modified.
- Adds a runtime dependency on the Google AI (Gemini) API: outbound HTTPS calls from the Odoo server, and an API key that must be stored as a protected system parameter, never committed to source control or logged.
- Introduces network-call latency and failure handling (timeouts, quota errors, invalid key) into the wizard's confirm action.
