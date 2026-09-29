from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    curp = fields.Char(string='CURP')
    cat_puesto_id = fields.Many2one(
        comodel_name='hr.cat.puesto',
        string='catPuiesto',
        ondelete='set null',
    )
    modalidad = fields.Char(string='Modalidad')
