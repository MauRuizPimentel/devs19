from odoo import api, fields, models

VEHICLE_TYPES = [
    ("car", "Automóvil"),
    ("truck", "Camión"),
    ("bicycle", "Bicicleta"),
    ("pet", "Mascota"),
]

VEHICLE_ICON_URLS = {
    "car": "/fleet_gps_tracker/static/src/img/car.svg",
    "truck": "/fleet_gps_tracker/static/src/img/truck.svg",
    "bicycle": "/fleet_gps_tracker/static/src/img/bicycle.svg",
    "pet": "/fleet_gps_tracker/static/src/img/pet.svg",
}


class GpsVehicle(models.Model):
    _name = "gps.vehicle"
    _description = "GPS Tracked Vehicle"

    name = fields.Char(string="Nombre", required=True)
    vehicle_type = fields.Selection(VEHICLE_TYPES, string="Tipo", required=True, default="car")
    icon = fields.Char(string="Ícono", compute="_compute_icon")
    coordinate_ids = fields.One2many("gps.coordinate", "vehicle_id", string="Puntos de Recorrido")
    latitude = fields.Float(string="Latitud", compute="_compute_current_position", digits=(10, 6), store=True)
    longitude = fields.Float(string="Longitud", compute="_compute_current_position", digits=(10, 6), store=True)
    last_recorded_at = fields.Datetime(
        string="Última Actualización", compute="_compute_current_position", store=True
    )
    has_position = fields.Boolean(string="Tiene Posición", compute="_compute_current_position", store=True)

    @api.depends("vehicle_type")
    def _compute_icon(self):
        for vehicle in self:
            vehicle.icon = VEHICLE_ICON_URLS.get(vehicle.vehicle_type, VEHICLE_ICON_URLS["car"])

    @api.depends("coordinate_ids.recorded_at", "coordinate_ids.latitude", "coordinate_ids.longitude")
    def _compute_current_position(self):
        for vehicle in self:
            last_point = vehicle.coordinate_ids[-1:]
            vehicle.latitude = last_point.latitude
            vehicle.longitude = last_point.longitude
            vehicle.last_recorded_at = last_point.recorded_at
            vehicle.has_position = bool(last_point)
