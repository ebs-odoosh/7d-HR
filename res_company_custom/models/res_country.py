from odoo import fields, models


class Country(models.Model):
    _inherit = 'res.country'

    arabic_name = fields.Char(string="Arabic Name")
