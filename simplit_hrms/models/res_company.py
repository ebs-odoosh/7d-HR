# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResCompany(models.Model):
	_inherit = 'res.company'


	company_code = fields.Char(string="Company Code")

	