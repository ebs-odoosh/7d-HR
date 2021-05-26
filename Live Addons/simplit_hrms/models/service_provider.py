from odoo import api, fields, models, _

class ServiceProvider(models.Model):
    _name = "service.provider"
    _description = "Service Provider"
    # _sql_constraints = [('name_uniq', 'unique (name)', "service provider already exists !")]

    name = fields.Char(string="Service Provider", required=True)


