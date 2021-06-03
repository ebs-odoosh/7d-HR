# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class HRRecruitmentQuestions(models.Model):
    _name = 'hr.recruitment.questions'
    _description = 'HR Recruitment Questions'

    name = fields.Char('Question', required=True)
    answer_ids = fields.One2many('hr.recruitment.answers', 'question_id', string='Answers')


class HRRecruitmentQuestionsAnswers(models.Model):
    _name = 'hr.recruitment.answers'
    _description = 'HR Recruitment Answers'

    @api.depends('application_id', 'question_id')
    def _compute_name(self):
        for record in self:
            if record.application_id and record.question_id:
                record.name = record.application_id.partner_name + ' [' + record.question_id.name + ' - ' + record.answer + ']'
            else:
                record.name = ''

    name = fields.Char(
        'Name', compute='_compute_name', store=True)
    application_id = fields.Many2one('hr.applicant', string='Applicant', required=True, ondelete='cascade')
    question_id = fields.Many2one('hr.recruitment.questions', string='Question', required=True, ondelete='cascade')
    answer = fields.Selection([('no', 'No'), ('yes', 'Yes')], default='no', string='Yes/No')
    details = fields.Text(string='Details')

    _sql_constraints = [
        ('applicant_question_uniq', 'unique (question_id,application_id)',
         'The question must be unique per applicant!')
    ]
