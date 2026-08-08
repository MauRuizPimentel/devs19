import json
import logging

import requests

from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

OPENWEATHERMAP_URL = "https://api.openweathermap.org/data/2.5/weather"
REQUEST_TIMEOUT = 10


class WeatherLookupWizard(models.TransientModel):
    _name = "weather.lookup.wizard"
    _description = "Weather Lookup Wizard"

    city_name = fields.Char(string="City", required=True)
    result_json = fields.Char(string="Result", readonly=True)

    def action_fetch_weather(self):
        self.ensure_one()
        api_key = self.env["res.config.settings"].get_openweathermap_api_key()

        try:
            response = requests.get(
                OPENWEATHERMAP_URL,
                params={"q": self.city_name, "units": "metric", "appid": api_key},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.RequestException:
            _logger.warning("OpenWeatherMap request failed for city %r", self.city_name)
            raise UserError(_("The weather service is temporarily unavailable. Please try again later."))

        if response.status_code != 200:
            api_message = ""
            try:
                api_message = response.json().get("message", "")
            except ValueError:
                pass
            _logger.warning(
                "OpenWeatherMap returned status %s for city %r: %s", response.status_code, self.city_name, api_message
            )
            detail = f": {api_message}" if api_message else ""
            if 400 <= response.status_code < 500:
                raise UserError(_("OpenWeatherMap could not process the request (HTTP %(status)s)%(detail)s.") % {
                    "status": response.status_code,
                    "detail": detail,
                })
            raise UserError(_("The weather service is temporarily unavailable (HTTP %(status)s)%(detail)s. Please try again later.") % {
                "status": response.status_code,
                "detail": detail,
            })

        payload = response.json()
        self.result_json = json.dumps(
            {
                "resolved_location": payload.get("name") or self.city_name,
                "country_code": payload.get("sys", {}).get("country") or "",
                "temperature": payload.get("main", {}).get("temp"),
                "condition_main": (payload.get("weather") or [{}])[0].get("main") or "",
                "condition_description": (payload.get("weather") or [{}])[0].get("description") or "",
            }
        )

        return {
            "type": "ir.actions.act_window",
            "res_model": "weather.lookup.wizard",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
