from odoo import models, fields, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # current_account_number = fields.Char(string='Current Account Number', compute='_compute_bank_details',
    #                                      readonly=True)
    # current_bank_name = fields.Many2one('res.bank', string='Current Bank Name', readonly=True)
    # iban = fields.Char(string="IBAN NO.", compute='_compute_bank_details')
    bank_history_ids = fields.One2many('employee.bank.change', 'employee_bank_change', string="Employee bank history")

    def _compute_bank_details(self):
        details = self.bank_history_ids
        if details:
            if len(details) == 1:
                self.current_bank_name = details.current_bank_name.id or ''
                self.iban = details.current_iban or ''
                self.current_account_number = details.current_account_number or ''
            elif len(details) > 1:
                last_rec = (len(details) - 1)
                self.current_bank_name = details[last_rec].current_bank_name.id or ''
                self.iban = details[last_rec].current_iban or ''
                self.current_account_number = details[last_rec].current_account_number or ''
        else:
            self.current_account_number = ''
            self.iban = ''
            return

    # def name_get(self):
    #     """
    #     :Author:Nimesh Jadav TechUltra Solutions
    #     :Date:24/11/2020
    #     :Func:this method use for the add name with with x_company_id id for approval request
    #     :Return:list with name and company id
    #     """
    #     result = []
    #     for employee in self:
    #         if self._context.get('active_model', False):
    #             if self._context.get('active_model') == "approval.category" or self._context.get(
    #                     'active_model') == "approval.request":
    #                 if employee.name:
    #                     result.append(
    #                         (employee.id, _(" %s  -  %s") % (
    #                             employee.sudo().namex_company_id)
    #                          ))
    #         else:
    #             result.append((employee.id, employee.sudo().name))
    #     return result
