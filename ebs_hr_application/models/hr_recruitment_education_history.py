# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class HRRecruitmentEducation(models.Model):
    _name = 'hr.recruitment.education.history'
    _description = 'HR Recruitment Education History'

    @api.depends('application_id.partner_name', 'type')
    def _compute_name(self):
        for record in self:
            if record.application_id.partner_name and record.type:
                record.name = record.application_id.partner_name + ' [' + record.type + ']'
            else:
                record.name = ''

    name = fields.Char(
        'Name', compute='_compute_name', store=True)

    education_place_name = fields.Char('Place Name', required=True)
    type = fields.Selection([('school', 'School'), ('university', 'University'), ('training', 'Training')],
                            string='Type', required=True, default='university')
    application_id = fields.Many2one('hr.applicant', string='Applicant', required=True, ondelete='cascade')
    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)
