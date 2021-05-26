# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    employement_type =  fields.Selection([
        ('full', 'Full Time'),
        ('partime', 'Part Time'),
        ('subcontractor', 'Sub Contractor'),
        ('freelancer', 'Freelancer'),
        ('project_base', 'Project Base')], 
        string="Employment Type")

    contract_type =  fields.Selection([
        ('contract_internal', 'Internal Contract'),
        ('contract_official', 'official Government Contract')], 
        string="Contract Type")

    sponsor_name = fields.Char(string="Sponsar Name") 
    company_sponsorship_license = fields.Integer(string="Company Sponsorship License")
    registration_number = fields.Integer(string="Registration Number")
    contract_duration = fields.Integer(string="Contract Duration")

    # swetha code
    contract_number = fields.Integer(string="Contract Number")
    car_gas_card_limit = fields.Integer(string="Car&Gas Card Limit")
    vendor_card_limit = fields.Integer(string="Vendor Card Limit")
    house_rent_allowance = fields.Boolean(string="House Rent Allowance")
    landlord_info = fields.Char(string="Landlord Information")
    contact_person = fields.Char(string="Contact Person")
    rent = fields.Integer(string="Rent Amount")
    contract_period = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years'),
    ], string='Contract Period', index=True, default='days')
    contract_period_duration = fields.Integer(string="Contract Period Duration")