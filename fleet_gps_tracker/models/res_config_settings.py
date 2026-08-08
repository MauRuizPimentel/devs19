from odoo import api, fields, models

API_KEY_PARAM = "fleet_gps_tracker.google_maps_api_key"


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    google_maps_api_key = fields.Char(
        string="Google Maps API Key",
        config_parameter=API_KEY_PARAM,
    )

    @api.model
    def get_google_maps_api_key(self):
        return self.env["ir.config_parameter"].sudo().get_param(API_KEY_PARAM) or ""
