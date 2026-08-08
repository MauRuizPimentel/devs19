import random
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

SAMPLE_INTERVAL_SECONDS = 30
MAX_DURATION_MINUTES = 30
STEP_DEGREES = 0.0008
# Fallback starting point (Mexico City) used only when the vehicle has no prior coordinate.
DEFAULT_SEED_LATITUDE = 19.432608
DEFAULT_SEED_LONGITUDE = -99.133209


class GpsSimulateWizard(models.TransientModel):
    _name = "gps.simulate.wizard"
    _description = "Simular Datos de Recorrido"

    vehicle_id = fields.Many2one("gps.vehicle", string="Vehículo", required=True)
    date = fields.Datetime(string="Fecha", required=True, default=fields.Datetime.now)
    duration_minutes = fields.Integer(string="Duración (minutos)", required=True, default=5)

    @api.constrains("duration_minutes")
    def _check_duration_minutes(self):
        for wizard in self:
            if not 1 <= wizard.duration_minutes <= MAX_DURATION_MINUTES:
                raise ValidationError(_("La duración debe estar entre 1 y %s minutos.") % MAX_DURATION_MINUTES)

    def action_simulate(self):
        self.ensure_one()
        last_point = self.vehicle_id.coordinate_ids[-1:]
        latitude = last_point.latitude if last_point else DEFAULT_SEED_LATITUDE
        longitude = last_point.longitude if last_point else DEFAULT_SEED_LONGITUDE

        num_points = (self.duration_minutes * 60) // SAMPLE_INTERVAL_SECONDS
        values = []
        for step in range(1, num_points + 1):
            latitude += random.uniform(-STEP_DEGREES, STEP_DEGREES)
            longitude += random.uniform(-STEP_DEGREES, STEP_DEGREES)
            values.append(
                {
                    "vehicle_id": self.vehicle_id.id,
                    "recorded_at": self.date + timedelta(seconds=step * SAMPLE_INTERVAL_SECONDS),
                    "latitude": latitude,
                    "longitude": longitude,
                }
            )
        self.env["gps.coordinate"].create(values)

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Simulación completa"),
                "message": _("%(count)s puntos generados para %(vehicle)s.")
                % {"count": len(values), "vehicle": self.vehicle_id.name},
                "type": "success",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
