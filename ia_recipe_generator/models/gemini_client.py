import json
import logging

import requests

from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

API_KEY_PARAM = "ia_recipe_generator.gemini_api_key"
MODEL_PARAM = "ia_recipe_generator.gemini_model"
CUSTOM_MODEL_PARAM = "ia_recipe_generator.gemini_model_custom"
CUSTOM_MODEL_VALUE = "custom"
DEFAULT_TEXT_MODEL = "gemini-3.6-flash"
MODEL_CHOICES = [
    ("gemini-3.6-flash", "Gemini 3.6 Flash"),
    ("gemini-3.5-flash", "Gemini 3.5 Flash"),
    ("gemini-3.5-flash-lite", "Gemini 3.5 Flash Lite"),
    ("gemini-2.5-flash", "Gemini 2.5 Flash (retiring Oct 2026)"),
    ("gemini-2.5-flash-lite", "Gemini 2.5 Flash Lite (retiring Oct 2026)"),
    (CUSTOM_MODEL_VALUE, "Custom..."),
]
API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
IMAGE_MODEL = "gemini-2.0-flash-preview-image-generation"
REQUEST_TIMEOUT = 30

RECIPE_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "name": {"type": "STRING"},
        "instructions": {"type": "STRING"},
        "preparation_time": {"type": "INTEGER"},
        "difficulty": {"type": "STRING", "enum": ["easy", "medium", "hard"]},
    },
    "required": ["name", "instructions", "preparation_time", "difficulty"],
}


class GeminiClient:
    """Thin wrapper around Google's Generative Language (Gemini) API."""

    def __init__(self, env):
        self.env = env

    def _get_api_key(self):
        api_key = self.env["ir.config_parameter"].sudo().get_param(API_KEY_PARAM)
        if not api_key:
            raise UserError(
                _("The Google AI (Gemini) API key is not configured. Ask an administrator to set it under Settings.")
            )
        return api_key

    def _get_text_model(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        model = ir_config.get_param(MODEL_PARAM) or DEFAULT_TEXT_MODEL
        if model == CUSTOM_MODEL_VALUE:
            model = ir_config.get_param(CUSTOM_MODEL_PARAM) or DEFAULT_TEXT_MODEL
        model = model.strip()
        if model.startswith("models/"):
            model = model[len("models/"):]
        return model

    def generate_recipe(self, food_name):
        """Call Gemini for a structured recipe. Raises UserError, naming the
        specific failure, on any request, HTTP, or parsing error."""
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "Give me a complete, realistic recipe for a dish matching this "
                                f"description: {food_name!r}. Write the recipe name and preparation "
                                "instructions in Spanish (español), regardless of the language of the "
                                "description. The difficulty field must still be exactly one of the "
                                "literal English values: easy, medium, or hard."
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": RECIPE_RESPONSE_SCHEMA,
            },
        }

        response = self._post(self._get_text_model(), payload, food_name)
        return self._parse_recipe_response(response)

    def generate_image(self, recipe_name):
        """Best-effort image generation. Never raises - returns base64 image
        data on success, or None on any failure."""
        try:
            api_key = self._get_api_key()
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": (
                                    "A high quality, appetizing photo of the following dish, "
                                    f"no text or watermarks: {recipe_name}."
                                )
                            }
                        ]
                    }
                ],
                "generationConfig": {"responseModalities": ["IMAGE"]},
            }
            url = f"{API_BASE_URL}/{IMAGE_MODEL}:generateContent"
            response = requests.post(url, params={"key": api_key}, json=payload, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            parts = response.json()["candidates"][0]["content"]["parts"]
            for part in parts:
                inline_data = part.get("inlineData") or part.get("inline_data") or {}
                if inline_data.get("data"):
                    return inline_data["data"]
            return None
        except Exception:
            _logger.warning("Gemini image generation failed for recipe %r", recipe_name, exc_info=True)
            return None

    def _post(self, model, payload, food_name):
        url = f"{API_BASE_URL}/{model}:generateContent"
        api_key = self._get_api_key()
        try:
            response = requests.post(url, params={"key": api_key}, json=payload, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as exc:
            _logger.warning("Gemini request failed for %r: %s", food_name, exc)
            raise UserError(
                _("Could not reach the Google AI API (%(error_type)s): %(error)s")
                % {"error_type": type(exc).__name__, "error": str(exc)}
            )

        if response.status_code != 200:
            raise UserError(self._format_http_error(response))

        return response

    def _format_http_error(self, response):
        status = ""
        message = ""
        try:
            error_payload = response.json().get("error", {})
            status = error_payload.get("status") or ""
            message = error_payload.get("message") or ""
        except ValueError:
            pass
        detail = " ".join(part for part in (status, message) if part)
        if detail:
            return _("Google AI API request failed (HTTP %(code)s %(detail)s)") % {
                "code": response.status_code,
                "detail": detail,
            }
        return _("Google AI API request failed (HTTP %(code)s)") % {"code": response.status_code}

    def _parse_recipe_response(self, response):
        try:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            recipe_data = json.loads(text)
            name = recipe_data["name"]
            instructions = recipe_data["instructions"]
            preparation_time = int(recipe_data["preparation_time"])
            difficulty = recipe_data["difficulty"]
            if difficulty not in ("easy", "medium", "hard"):
                raise ValueError("unexpected difficulty value: %r" % difficulty)
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            _logger.warning("Malformed Gemini response: %s", exc)
            raise UserError(
                _("The Google AI API returned a malformed or unexpected response (%(error_type)s).")
                % {"error_type": type(exc).__name__}
            )

        return {
            "name": name,
            "instructions": instructions,
            "preparation_time": preparation_time,
            "difficulty": difficulty,
        }
