from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError


class TravelRequestSettings(models.Model):
    _name = 'travel.request.settings'
    _description = 'Travel Request Settings'
    _order = 'id desc'

    def _default_perdiem_product(self):
        """
        :Author: Bhavesh Jadav TechUltra solutions
        :Date: 17/10/2020
        :Func: This method sye for the set per diam product when form open
        :Return:product id or False
        """
        product = self.env.ref('employee_travel_management.expense_product_14') or False
        if product:
            return product.id
        return False

    name = fields.Char(string="Name")
    approval_minimum = fields.Integer(string="Minimum Approval", default="1", required=True)
    travel_agency_ids = fields.Many2many('res.partner', 'travel_request_settings_rel', 'partner_id',
                                         'agency_setting_id',
                                         string="Travel Agencies", copy=True)
    approver_ids = fields.Many2many('res.users', 'travel_request_settings_user_rel', 'user_id', 'approver_id',
                                    copy=True)
    default_approver = fields.Many2one('res.users', string="Admin Approver", required=True, default=2, copy=True)
    approval_sequence = fields.One2many('travel.approval.sequence', 'related_travel_setting', 'Approval Sequence',
                                        copy=True)
    email_from = fields.Char(string="Set Email From")
    reply_to = fields.Char(string="Set Reply To")
    perdiem_rule_lines = fields.One2many('travel.perdiem.rule', 'travel_settings_id', copy=True)
    perdiem_expense_product = fields.Many2one('product.product', string="Perdiem Expense Product",
                                              default=_default_perdiem_product, copy=True)
    is_manager_approver = fields.Boolean(string="Is Manager Approver")
    is_higher_manager_approver = fields.Boolean(string="Is Higher Manager Approver")

    @api.onchange('is_manager_approver')
    def onchange_is_manager_approver(self):
        if self.is_manager_approver:
            self.approval_sequence = [(0, 0, {
                'approval_category': 'LM-1',
                'is_manager_approver': True
            })]
        else:
            manager = self.approval_sequence.filtered(lambda x: x.is_manager_approver == True)
            if manager:
                manager.unlink()

    @api.onchange('is_higher_manager_approver')
    def onchange_is_higher_manager_approver(self):
        if self.is_higher_manager_approver:
            self.approval_sequence = [(0, 0, {
                'approval_category': 'LM-2',
                'is_higher_manager_approver': True
            })]
        else:
            higher_manager = self.approval_sequence.filtered(lambda x: x.is_higher_manager_approver == True)
            if higher_manager:
                higher_manager.unlink()

    @api.model
    def create(self, vals):
        """
        :Author: Bhavesh Jadav TechUltra solutions
        :Date:09/10/2020
        :Func: inherit for the raise UserError if the per diam rule line was not created
        :Return:result of the supper call
        """
        if not vals.get('perdiem_rule_lines'):
            raise UserError(
                _("Please add Per Diem Rule Line"))
        return super(TravelRequestSettings, self).create(vals)


class PerDiemRule(models.Model):
    _name = 'travel.perdiem.rule'
    _description = 'Travel PerDiem Rule Settings'
    _order = 'id desc'

    name = fields.Char(string='Name')
    job_grade_ids = fields.Many2many('job.grade', string="Job Grades")
    min_days = fields.Integer(string="Min Days")
    max_days = fields.Integer(string="Max Days")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda x: x.env.company.currency_id)
    amount = fields.Float(string="Amount", currency_field='currency_id')
    accommodation_by_self_percentage = fields.Float(string="EE Accommodation(%)")
    accommodation_by_company_percentage = fields.Float(string="ER Accommodation(%)")
    active = fields.Boolean(string="Active", default=True)
    travel_settings_id = fields.Many2one('travel.request.settings', string="Travel Setting")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    class_of_travel = fields.Selection(
        selection=[('economy_class', 'Economy Class'), ('premium_economy_class', 'Premium Economy Class'),
                   ('business_class', 'Business Class')], default='economy_class')

    @api.model
    def create(self, vals):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date: 13/10/2020
        :Func: inherit for the raise UserError for the Duplicate Rule found and the wrong percentage entered
        :Return: Result of the supper call  Supper Call
        """
        if vals.get('accommodation_by_self_percentage') and vals.get(
                'accommodation_by_self_percentage') > 100 or vals.get(
            'accommodation_by_company_percentage') \
                and vals.get('accommodation_by_company_percentage') > 100:
            raise UserError(
                _("Please add proper percentage entered  percentage is more then 100"))
        vals['name'] = self.env['ir.sequence'].next_by_code('travel.perdiem.rule') or _('New')
        perdiem_rule = self.search_read(
            domain=[('min_days', '=', self.min_days), ('max_days', '=', self.max_days)], fields=['id'])
        if perdiem_rule:
            raise UserError(
                _("Duplicate Rule found please check conditions of the all rule"))
        res = super(PerDiemRule, self).create(vals)
        return res


class TravelApprovalSequence(models.Model):
    _name = 'travel.approval.sequence'
    sequence = fields.Integer('Sequence', default=10)
    user_id = fields.Many2one('res.users', 'Approver')
    related_travel_setting = fields.Many2one('travel.request.settings', 'Related Travel Setting')
    approval_category = fields.Char(string="Category")
    is_manager_approver = fields.Boolean(string="Is Manager Approver")
    is_higher_manager_approver = fields.Boolean(string="Is Higher Manager Approver")
