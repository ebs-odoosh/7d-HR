# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class HRDepartment(models.Model):
    _inherit = 'hr.department'
    _order = "complete_name"

    name_ar = fields.Char('Department Arabic Name')
