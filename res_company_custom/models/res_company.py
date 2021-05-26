from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'
    arabic_name = fields.Char(string="Arabic Name")
    arabic_street = fields.Char(string="Arabic Street")
    arabic_street2 = fields.Char(string="Arabic Street2")
    arabic_city_name = fields.Char(string="Arabic City Name")
    arabic_state_name = fields.Char(string="Arabic State Name")
    footer_logo = fields.Binary(string="Footer Logo")
    header_logo = fields.Binary(string="Header Logo")
