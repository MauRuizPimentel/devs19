from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

API_KEY_PARAM = "weather_api.openweathermap_api_key"


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    openweathermap_api_key = fields.Char(
        string="OpenWeatherMap API Key",
        config_parameter=API_KEY_PARAM,
    )

    @api.model
    def get_openweathermap_api_key(self):
        api_key = self.env["ir.config_parameter"].sudo().get_param(API_KEY_PARAM)
        if not api_key:
            raise UserError(
                _("The OpenWeatherMap API key is not configured. Ask an administrator to set it under Settings.")
            )
        return api_key
