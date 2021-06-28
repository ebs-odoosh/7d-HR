# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class HRRecruitmentLanguages(models.Model):
    _name = 'hr.recruitment.language'
    _description = 'HR Recruitment Language'

    @api.depends('application_id.partner_name', 'language_id.name')
    def _compute_name(self):
        for record in self:
            if record.application_id.partner_name and record.language_id.name:
                record.name = record.application_id.partner_name + ' [' + record.language_id.name + ']'
            else:
                record.name = ''

    name = fields.Char(
        'Name', compute='_compute_name', store=True)
    reading = fields.Selection([('fluent', 'Fluent'), ('average', 'Average'), ('low', 'Low')],
                               string='Reading', required=True, default='average')
    writing = fields.Selection([('fluent', 'Fluent'), ('average', 'Average'), ('low', 'Low')],
                               string='Writing', required=True, default='average')
    spoken = fields.Selection([('fluent', 'Fluent'), ('average', 'Average'), ('low', 'Low')],
                              string='Spoken', required=True, default='average')
    language_id = fields.Many2one('hr.recruitment.language.data', required=True)
    application_id = fields.Many2one('hr.applicant', string='Applicant', required=True, ondelete='cascade')


class HRRecruitmentLanguagesData(models.Model):
    _name = 'hr.recruitment.language.data'
    _description = 'HR Recruitment Language Data'

    name = fields.Char(string='Name', required=True)
