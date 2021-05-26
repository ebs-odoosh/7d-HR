from odoo import fields, models, api


class EmploymentType (models.Model):
    _inherit = 'hr.employment.type'

    oc_color = fields.Integer("OC Color", default=0)
    


