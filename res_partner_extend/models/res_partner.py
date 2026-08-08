from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    birthdate = fields.Date(string="Fecha de nacimiento")
    age = fields.Integer(string="Edad", compute="_compute_age", store=True)

    @api.depends("birthdate")
    def _compute_age(self):
        """
        Compute the partner's age in full years from ``birthdate``.

        Partners without a ``birthdate``, or with a ``birthdate`` in the
        future, get an age of ``0`` instead of raising an error.

        :return: None (writes to ``age`` on each record in ``self``)
        :rtype: None
        """
        today = fields.Date.context_today(self)
        for partner in self:
            if not partner.birthdate or partner.birthdate > today:
                partner.age = 0
            else:
                partner.age = relativedelta(today, partner.birthdate).years

    def _cron_update_age(self):
        """
        Refresh the stored ``age`` of partners whose value is stale.

        Since ``age`` is a stored computed field, it is only recalculated
        when ``birthdate`` changes or the record is written. This method
        is meant to run on a daily :class:`ir.cron` so that partners who
        are not edited on their birthday still get an up-to-date ``age``.
        Only partners whose computed age differs from the stored value are
        recomputed, to avoid unnecessary writes.

        :return: None
        :rtype: None
        """
        partners = self.search([("birthdate", "!=", False)])
        stale = partners.filtered(
            lambda p: p.age != relativedelta(
                fields.Date.context_today(p), p.birthdate
            ).years
        )
        if stale:
            stale._compute_age()
