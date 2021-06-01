from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    product_id = fields.Many2one('product.product', string='Expense Type', readonly=True,
                                 states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                                         'refused': [('readonly', False)]},
                                 domain="[('is_per_diem_product', '=', False),('can_be_expensed', '=', True), '|', "
                                        "('company_id', '=', False), ('company_id', '=', company_id)]",
                                 ondelete='restrict')
    name = fields.Char('Purpose', readonly=True, required=True,
                       states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                               'refused': [('readonly', False)]})

    expense_type = fields.Many2one('expense.type', string="Expense Category")

    expense_cost_center_lines = fields.One2many('expense.cost.center.line', 'expense_id',
                                                string="Expense Cost Center Line", track_visibility='onchange',
                                                required=True)

    @api.onchange('expense_type')
    def _onchange_expense_type(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:  21/01/2021
        Func: for apply dynamic domain
        :return: domain
        """
        product_ids = self.env['product.product']
        if self.expense_type:
            product_ids = self.env['product.product'].search(
                [('can_be_expensed', '=', True), ('expense_type', 'in', self.expense_type.ids)])
        return {'domain': {'product_id': [('id', 'in', product_ids.ids)]}}

    def _create_sheet_from_expenses(self):
        sheet = super(HrExpense, self)._create_sheet_from_expenses()
        sheet._onchange_expense_settings_id()
        return sheet

    @api.onchange('employee_id')
    def onchange_employee_info(self):
        for rec in self:
            if rec.employee_id:
                employee_cost_center = rec.employee_id.contract_id.cost_center
                rec.expense_cost_center_lines = False
                if employee_cost_center:
                    new_cc_line = [(0, 0, {
                        'cost_center_id': employee_cost_center,
                        'share_percentage': 100})]
                    rec.expense_cost_center_lines = new_cc_line

    @api.model
    def create(self, vals):
        if not vals.get('expense_cost_center_lines'):
            if vals.get('product_id'):
                product_id = self.env['product.product'].browse(vals.get('product_id'))
                if product_id and not product_id.is_per_diem_product:
                    raise UserError(
                        _("Please add Expense Cost Center line"))
        res = super(HrExpense, self).create(vals)
        return res
    #
    # aed_currency = fields.Many2one('res.currency', string="AED Currency",
    #                                compute='_compute_currency_in_aed')
    #
    # amount_in_aed = fields.Monetary(string="Total in AED", compute='_compute_amount_in_aed',
    #                                 currency_field='aed_currency')

    # @api.depends('currency_id')
    # def _compute_currency_in_aed(self):
    #     for rec in self:
    #         rec.aed_currency = self.env['res.currency'].search([('name', '=', 'AED')])
    #
    # @api.depends('total_amount')
    # def _compute_amount_in_aed(self):
    #     """
    #     @Author:Bhavesh Jadav TechUltra Solutions
    #     @Date:18/01/2021
    #     @Func:This compute method use for the convert the  currency in AED
    #     @Return:N/A
    #     """
    #     for rec in self:
    #         rec.amount_in_aed = rec.total_amount
    #         currency_id = rec.currency_id
    #         aed_currency_id = self.env['res.currency'].search([('name', '=', 'AED')])
    #         rec.amount_in_aed = aed_currency_id.compute(rec.total_amount, currency_id)
