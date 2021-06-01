from odoo import models, fields, api, _


class TravelExpenseLine(models.Model):
    _name = 'travel.expense.line'
    _description = 'Travel Expense Line'
    _order = 'id desc'

    name = fields.Char(string="Name")
    product_id = fields.Many2one('product.product', string="Product")
    unit_amount = fields.Float(string="Unit Price")
    quantity = fields.Float(string="Quantity")
    date = fields.Date(string="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    note = fields.Text(string="Note")
