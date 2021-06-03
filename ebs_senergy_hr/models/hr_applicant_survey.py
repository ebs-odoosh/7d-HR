# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ApplicantSurveys(models.Model):
    _inherit = 'hr.applicant.survey'

    done_date = fields.Date(string='Interview Date', related="response_id.done_date")
    done_time = fields.Float(string='Interview Time', related="response_id.done_time")
    stage_id = fields.Many2one(related="related_applicant.stage_id", string='Status')
    partner_name = fields.Char(related="related_applicant.partner_name", string="Applicant's Name")
    job_id = fields.Many2one(related="related_applicant.job_id", string="Applied Job")
    user_id = fields.Many2one(related="response_id.create_uid", string='Interviewer')
