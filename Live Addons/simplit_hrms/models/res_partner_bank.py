from odoo import api, fields, models, _

class HrEmployee(models.Model):
	_inherit = 'res.bank'
	
	branch_name = fields.Char(string="Employee Bank Branch")