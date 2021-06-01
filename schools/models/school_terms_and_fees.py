from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SchoolTermsFees(models.Model):
    _name = 'school.terms.fees'
    _description = "School Terms  and Fees"
    _order = 'id'

    # Added By Bhavesh Jadav
    name = fields.Char(string='Name')
    note = fields.Text(string="Note")
