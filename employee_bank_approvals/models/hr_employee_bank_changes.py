# -*- coding: utf-8 -*-

from odoo import models, fields


class EmployeeBankChanges(models.Model):
    _name = 'employee.bank.change'
    _description = 'Employee Bank Account'

    employee_bank_change = fields.Many2one('hr.employee', string="Employee Name")
    # employee_number = fields.Char(related='employee_bank_change.x_company_id', string="Employee Number")
    department_id_e_bank = fields.Many2one(related='employee_bank_change.contract_id.department', string="Department")
    date_of_join_e_bank = fields.Date(related='employee_bank_change.contract_id.date_start', string="Date of joining")
    current_bank_name = fields.Many2one('res.bank', string='Current Bank Name')
    current_iban = fields.Char(string='Current IBAN')
    current_account_number = fields.Char(string='Current Account Number')
    account_number = fields.Char(string='Old Account Number')
    iban = fields.Char(string='Old IBAN')
    # effective_month_year = fields.Date(string='Effective Date')
    select_bank = fields.Many2one('res.bank', string='Old Bank Name')
    # effective_date = fields.Char('Effective Month', store=True)
    effective_month_year = fields.Char('Effective Month/Year', store=True)
    bank_change_approval = fields.Many2one('approval.request', 'Approval Request')
    attachment = fields.Binary(string="Attachment", readonly=True)
    limit_month_day = fields.Integer(string="Limit day of month", readonly=True)

    def name_get(self):
        """
        :Author:Nimesh Jadav TechUltra Solutions
        :Date:07/10/2020
        :Func:this method use for the add name in name the field
        :Return:list with name and
        """
        result = []
        for employee in self:
            if employee.employee_bank_change:
                name = employee.employee_bank_change.name
                result.append((employee.id, name))
        return result
