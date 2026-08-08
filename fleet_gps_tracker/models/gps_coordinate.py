from odoo import fields, models


class GpsCoordinate(models.Model):
    _name = "gps.coordinate"
    _description = "GPS Coordinate Point"
    _order = "recorded_at asc"

    vehicle_id = fields.Many2one(
        "gps.vehicle", string="Vehículo", required=True, ondelete="cascade", index=True
    )
    recorded_at = fields.Datetime(string="Fecha y Hora", required=True, index=True)
    latitude = fields.Float(string="Latitud", required=True, digits=(10, 6))
    longitude = fields.Float(string="Longitud", required=True, digits=(10, 6))

    def get_route(self, vehicle_id, date_from, date_to):
        return self.search(
            [
                ("vehicle_id", "=", vehicle_id),
                ("recorded_at", ">=", date_from),
                ("recorded_at", "<=", date_to),
            ]
        )
