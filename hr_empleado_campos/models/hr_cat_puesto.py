from odoo import fields, models


class HrCatPuesto(models.Model):
    _name = 'hr.cat.puesto'
    _description = 'Catálogo de puestos'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
