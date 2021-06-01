from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError


class HrExpenseSettings(models.Model):
    _name = 'hr.expense.settings'
    _description = 'Hr Expense Settings'
    _order = 'id desc'

    name = fields.Char(string="Name")
    approval_minimum = fields.Integer(string="Minimum Approval", default="1", required=True)
    approver_ids = fields.Many2many('res.users', 'hr_expense_settings_user_rel', 'user_id', 'approver_id')
    approval_sequence = fields.One2many('hr.expense.approval.sequence', 'related_hr_expense_setting',
                                        'Approval Sequence')
    is_travel_expense_approval = fields.Boolean(string="Is Travel Expense Approval", default=False)

    expense_type = fields.Many2many('expense.type', 'expense_settings_expense_type_rel', 'setting_id',
                                    'type_id', string="Expense Category")

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


class HrExpenseApprovalSequence(models.Model):
    _name = 'hr.expense.approval.sequence'
    sequence = fields.Integer('Sequence', default=10)
    user_id = fields.Many2one('res.users', 'Approver')
    related_hr_expense_setting = fields.Many2one('hr.expense.settings', 'Related Hr Expense Setting')
    approval_category = fields.Char(string="Category")

    is_manager_approver = fields.Boolean(string="Is Manager Approver")
    is_higher_manager_approver = fields.Boolean(string="Is Higher Manager Approver")


class HrExpenseApprover(models.Model):
    _name = 'hr.expense.approver'
    _description = 'Hr Expense Approver'

    user_id = fields.Many2one('res.users', string="User", required=True)
    status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], string="Status", default="new", readonly=True)
    expense_sheet_id = fields.Many2one('hr.expense.sheet', string="Expense Sheet", ondelete='cascade')
    reject_reason = fields.Char('Rejection Reason')
    sequence = fields.Integer('Sequence', default=10)
    approval_date = fields.Datetime(
        string='Approval Date',
        required=False, readonly=True)
    approval_category = fields.Char(string="Category")

    @api.onchange('user_id')
    def _onchange_approver_ids(self):
        return {'domain': {'user_id': [('id', 'not in', self.expense_sheet_id.approver_ids.mapped(
            'user_id').ids + self.expense_sheet_id.create_uid.ids)]}}

    def _create_activity(self):
        for approver in self:
            approver.expense_sheet_id.activity_schedule(
                'hr_expense.mail_act_expense_approval',
                user_id=approver.user_id.id)

    def unlink(self):
        activity = self.env.ref('hr_expense.mail_act_expense_approval').id
        activities = self._get_user_approval_activities(user=self.user_id, res_ids=self.expense_sheet_id.ids,
                                                        activity_type_id=activity)
        activities.unlink()
        res = super(HrExpenseApprover, self).unlink()
        return res

    def _get_user_approval_activities(self, user, res_ids, activity_type_id):
        domain = [
            ('res_model', '=', 'hr.expense.sheet'),
            ('res_id', 'in', res_ids),
            ('activity_type_id', '=', activity_type_id),
            ('user_id', '=', user.id)
        ]
        activities = self.env['mail.activity'].search(domain)
        return activities

    @api.model
    def create(self, vals):
        res = super(HrExpenseApprover, self).create(vals)
        if len(res.expense_sheet_id.approver_ids.filtered(
                lambda approver: approver.status == 'pending')) > 1:
            raise UserError(_("You Can not add Multiple approve with 'To Approve' Status."))
        next_approvers = self.env['hr.expense.sheet'].browse(vals['expense_sheet_id']).approver_ids
        next_approver = next_approvers.filtered(lambda approver: approver.status == 'pending').sorted(
            'sequence')
        if next_approver:
            next_approver[0]._create_activity()
        return res
