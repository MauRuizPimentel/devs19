from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _


class GpsPlaybackWizard(models.TransientModel):
    _name = "gps.playback.wizard"
    _description = "Generar Recorrido"

    vehicle_id = fields.Many2one("gps.vehicle", string="Vehículo", required=True)
    date_from = fields.Datetime(string="Fecha Inicial", required=True)
    date_to = fields.Datetime(string="Fecha Final", required=True)

    @api.constrains("date_from", "date_to")
    def _check_date_range(self):
        for wizard in self:
            if wizard.date_from and wizard.date_to and wizard.date_to <= wizard.date_from:
                raise ValidationError(_("La fecha final debe ser posterior a la fecha inicial."))

    def action_generate_route(self):
        self.ensure_one()
        points = self.env["gps.coordinate"].get_route(self.vehicle_id.id, self.date_from, self.date_to)
        if not points:
            raise UserError(_("No hay datos de recorrido para el vehículo y rango seleccionados."))

        return {
            "type": "ir.actions.client",
            "tag": "fleet_gps_tracker.route_playback",
            "name": _("Recorrido: %s") % self.vehicle_id.name,
            "params": {
                "vehicle_name": self.vehicle_id.name,
                "vehicle_icon": self.vehicle_id.icon,
                "points": [{"lat": point.latitude, "lng": point.longitude} for point in points],
            },
        }
