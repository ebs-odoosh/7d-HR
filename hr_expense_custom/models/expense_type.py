from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError


class ExpenseType(models.Model):
    _name = 'expense.type'
    _description = 'Expense Type'
    _order = 'id desc'

    name = fields.Char(string="Name")
    expense_type_code = fields.Char(string="Code")

    @api.model
    def create(self, vals):
        if vals.get('expense_type_code') and self.search_read(
                [('expense_type_code', '=', vals.get('expense_type_code'))], ['id']):
            raise UserError(_('Duplicate code! Please add unique code for the New Expense Type'))
        res = super(ExpenseType, self).create(vals)
        return res
