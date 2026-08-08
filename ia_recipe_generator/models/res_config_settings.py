from odoo import fields, models

from .gemini_client import (
    API_KEY_PARAM,
    CUSTOM_MODEL_PARAM,
    CUSTOM_MODEL_VALUE,
    DEFAULT_TEXT_MODEL,
    MODEL_CHOICES,
    MODEL_PARAM,
)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    gemini_api_key = fields.Char(
        string="Google AI (Gemini) API Key",
        config_parameter=API_KEY_PARAM,
    )
    # gemini_model intentionally does NOT use config_parameter=: Odoo's automatic
    # binding writes/reads the raw ir.config_parameter value without validating it
    # against the Selection's choices, so a stale or free-typed value (e.g. left over
    # from before this field existed) crashes the settings form on load. get_values()/
    # set_values() below validate it instead, falling back to "custom" when it doesn't
    # match a known choice.
    gemini_model = fields.Selection(MODEL_CHOICES, string="Gemini Model", default=DEFAULT_TEXT_MODEL)
    gemini_model_custom = fields.Char(string="Custom Model ID")

    def get_values(self):
        res = super().get_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        stored_model = ir_config.get_param(MODEL_PARAM) or DEFAULT_TEXT_MODEL
        if stored_model in dict(MODEL_CHOICES):
            res["gemini_model"] = stored_model
            res["gemini_model_custom"] = ir_config.get_param(CUSTOM_MODEL_PARAM) or ""
        else:
            res["gemini_model"] = CUSTOM_MODEL_VALUE
            res["gemini_model_custom"] = stored_model
        return res

    def set_values(self):
        super().set_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        ir_config.set_param(MODEL_PARAM, self.gemini_model or DEFAULT_TEXT_MODEL)
        ir_config.set_param(CUSTOM_MODEL_PARAM, self.gemini_model_custom or "")
