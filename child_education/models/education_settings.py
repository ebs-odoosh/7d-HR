from odoo import models, fields, api, _


class EducationSettings(models.Model):
    _name = 'education.request.settings'
    _description = "Education  Settings"
    _order = 'id desc'

    name = fields.Char(string="Name")
    approval_minimum = fields.Integer(string="Minimum Approval", default="1", required=True)
    approver_ids = fields.Many2many('res.users', 'education_request_settings_user_rel', 'user_id', 'approver_id',
                                    copy=True)
    approval_sequence = fields.One2many('education.approval.sequence', 'related_education_setting', 'Approval Sequence',
                                        copy=True)
    is_manager_approver = fields.Boolean(string="Is Manager Approver")
    is_higher_manager_approver = fields.Boolean(string="Is Higher Manager Approver")


class EducationApprovalSequence(models.Model):
    _name = 'education.approval.sequence'
    sequence = fields.Integer('Sequence', default=10)
    user_id = fields.Many2one('res.users', 'Approver')
    related_education_setting = fields.Many2one('education.request.settings', 'Related Education Setting')
    approval_category = fields.Char(string="Category")
    is_hc_admin = fields.Boolean('HC Admin')
