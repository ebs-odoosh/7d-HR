# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HRRecruitmentReferences(models.Model):
    _name = 'hr.recruitment.references'
    _description = 'HR Recruitment References'

    name = fields.Char('Name')
    position_held = fields.Char(string='Position Held', required=True)
    email = fields.Char(string='Email', tracking=True)
    phone = fields.Char(string='Telephone no', tracking=True)
    previous_work_exp = fields.Boolean('Previous Work Experience')
    no_of_years_known = fields.Integer('No. of years known')
    # Address fields
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country')

    application_id = fields.Many2one('hr.applicant', string='Applicant', required=True, ondelete='cascade')
