from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    is_travel_agency = fields.Boolean(string="Is Travel Agency", default=False)
