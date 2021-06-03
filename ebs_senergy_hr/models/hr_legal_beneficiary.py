# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class LegalBeneficiary(models.Model):
    _name = 'legal.beneficiary'
    _description = 'Legal Beneficiary'

    name = fields.Char('Name', required=True)
    relationship = fields.Char('RelationShip', required=True)
    details = fields.Char('Details')
    application_id = fields.Many2one('hr.applicant', string='Applicant', required=True, ondelete='cascade')
