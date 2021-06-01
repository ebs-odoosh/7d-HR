# -*- coding: utf-8 -*-

from odoo import models, fields

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')]


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    has_employee_name = fields.Selection(CATEGORY_SELECTION, string="Name", default="no", required=True)
    has_employee_number = fields.Selection(CATEGORY_SELECTION, string="Employee Number", default="no", required=True)
    has_department_id_e_bank = fields.Selection(CATEGORY_SELECTION, string="Department", default="no", required=True)
    has_date_of_join_e_bank = fields.Selection(CATEGORY_SELECTION, string="Date of joining", default="no",
                                               required=True)
    has_current_bank_name = fields.Selection(CATEGORY_SELECTION, string="Current Bank Name", default="no",
                                             required=True)
    has_current_iban = fields.Selection(CATEGORY_SELECTION, string="Current IBAN", default="no", required=True)
    has_current_account_number = fields.Selection(CATEGORY_SELECTION, string="Current Account Number", default="no",
                                                  required=True)
    has_account_number = fields.Selection(CATEGORY_SELECTION, string="Account Number", default="no", required=True)
    has_iban = fields.Selection(CATEGORY_SELECTION, string="IBAN", default="no", required=True)
    has_effective_month_year = fields.Selection(CATEGORY_SELECTION, string="Effective Month/Year", default="no",
                                                required=True)
    has_select_bank = fields.Selection(CATEGORY_SELECTION, string="Select Bank", default="no", required=True)
    has_your_company = fields.Selection(CATEGORY_SELECTION, string="Company", default="no", required=True)
    is_bank_changes_request = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Is Bank Changes Request", default="no", required=True)
    has_limit_month_days = fields.Integer(string="Limit day of month", default=10)
