from odoo import fields, models, api


class ColorClass (models.Model):
    _name = 'color.class'
    _description = 'Description'

    name = fields.Char(string="Class Name", required=True)
    color = fields.Char(string='Hexadecimal Color', required=True)



