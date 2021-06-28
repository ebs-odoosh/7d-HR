# -*- coding: utf-8 -*-

from odoo import fields, models


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    relocate_current_job_title = fields.Many2one('job.title', string='Current vacant position')
    requisition_type = fields.Selection([
        ('replace', 'Replacement Position'),
        ('reallocated', 'Reallocated Position'),
        ('new', 'Budgeted New Position'),
        ('non_budget', 'Nonbudgeted New Position')
    ], string='Requisition Type')
    pay_grade_rage = fields.Float('Pay Grad/Range')
    current_pay_grade_rage = fields.Float('Current Pay Grad/Range')
    recommended_pay_grade_rage = fields.Float('Recommended pay grade/range')
    justify_non_budget_new_position = fields.Text('Justify how are you going to cover the nonbudgeted position cost.')
    special_adv = fields.Text('Special advertising')
    job_type = fields.Selection([
        ('full', 'Full Time'),
        ('part', 'Part Time')
    ], string='Job Type')
    military_status = fields.Selection([
        ('exempt', 'Exempt'),
        ('nonexempt', 'Nonexempt')
    ], string='Military Status')
    salary_type = fields.Selection([
        ('salaried', 'Salaried'),
        ('hourly', 'Hourly')
    ], string='Salary Type')
    preferred_date = fields.Date('Preferred Start Date')
    have_duties = fields.Boolean('Have the duties of this position changed?')
