from odoo import api, fields, models, _
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_expense_allowance(self, payslip):
        """
        @Author:Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date:28/01/2021
        @Func:this method use for add expense amount payslip
        @return: expense amount
        """
        date_from_month = payslip.date_from.strftime("%m")
        date_from_year = payslip.date_from.strftime("%Y")
        employee_id = self.env['hr.employee'].browse(payslip.employee_id)
        expense = 0.0
        hr_expense_sheet_ids = self.env['hr.expense.sheet'].search(
            [('employee_id', '=', employee_id.id),
             ('create_date', '>=', payslip.date_from), ('create_date', '<=', payslip.date_to),
             ('state', '=', 'approve'), ('payment_mode', '=', 'own_account')])
        for hr_expense_sheet_id in hr_expense_sheet_ids:
            expense += hr_expense_sheet_id.total_amount
        return expense

    def rule_applicable_condition_allowance_for_expense(self, payslip):
        """
        @Author: Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date:28/01/2021
        @Func:this method use for the check Expense rule applicable for that employee or not
        @return: true or false
        """
        date_from_month = payslip.date_from.strftime("%m")
        date_to_month = payslip.date_to.strftime("%m")
        date_from_year = payslip.date_from.strftime("%Y")
        if date_from_month == date_to_month:
            employee_id = self.env['hr.employee'].browse(payslip.employee_id)
            hr_expense_sheet_ids = self.env['hr.expense.sheet'].search(
                [('employee_id', '=', employee_id.id),
                 ('create_date', '>=', payslip.date_from), ('create_date', '<=', payslip.date_to),
                 ('state', '=', 'approve'), ('payment_mode', '=', 'own_account')])
            if hr_expense_sheet_ids:
                return True
            else:
                return False
        else:
            return False
