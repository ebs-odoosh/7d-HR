# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class HRRecruitmentEmploymentHistory(models.Model):
    _name = 'hr.recruitment.employment.history'
    _description = 'HR Recruitment Employment History'

    @api.depends('application_id.partner_name', 'company_name')
    def _compute_name(self):
        for record in self:
            if record.application_id.partner_name and record.company_name:
                record.name = record.application_id.partner_name + ' [' + record.company_name + ']'
            else:
                record.name = ''

    name = fields.Char(
        'Name', compute='_compute_name', store=True)
    company_name = fields.Char('Company Name', required=True)
    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To')
    type_of_job = fields.Text(string='Type of job and Responsibilities', required=True)
    reason_for_leaving = fields.Text(string='Reason for Leaving')
    current_job = fields.Boolean('Current Job')
    # Address fields
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country')

    application_id = fields.Many2one('hr.applicant', string='Applicant', required=True, ondelete='cascade')
    years_of_exp = fields.Float('Years of Exp', compute='_compute_years_of_exp')

    @api.depends('date_to', 'date_from')
    def _compute_years_of_exp(self):
        for record in self:
            if record.date_to and record.date_from:
                experience = (record.date_to - record.date_from)
                record.years_of_exp = experience.days / 365.2425
            elif record.date_from:
                experience = (fields.Date.context_today(self) - record.date_from)
                record.years_of_exp = experience.days / 365.2425
            else:
                record.years_of_exp = 0.0
