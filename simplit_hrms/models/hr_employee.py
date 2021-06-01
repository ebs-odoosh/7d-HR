# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    emp_sequence_id = fields.Char('Sequence', readonly=True)
    internal_emp_number = fields.Char(string="Employee Number")
    passport_issue_date = fields.Date(string="Passport Issue Date")
    passport_issuing_country =fields.Many2one('res.country')
    passport_expiry_date = fields.Date(string="Passport Expiry Date")

    visa_residency_type =  fields.Selection([
        ('equity', 'Equity')], string="Visa Residency Type")

    visa_residency_validity_from =fields.Date(string="Visa Residency Validity From")
    visa_residency_validity_to = fields.Date(string="Visa Residency Validity From")

    emp_bank_name  = fields.Char(string="Employee Bank Name")
    emp_branch = fields.Char(string="Employee Bank Branch")
    emp_account_number = fields.Integer(string="Employee Account Number")
    civil_id_number = fields.Char(string="Civil ID Number")
    civil_id_expiry = fields.Date(string="Civil ID Expiry")

    driving_license_number = fields.Integer(string="Driving Card Number")
    iban = fields.Integer(string="IBAN")
    health_card_number = fields.Integer(string="Health Card Number")
    health_card_validity = fields.Date(string="Civil ID Expiry")

    mobile_number = fields.Char(string="Mobile")
    mobile_bill_limit = fields.Integer(string="Mobile Bill Limit")
    service_provider_id = fields.Many2one('service.provider', string="Service Provider")
    data = fields.Boolean(string="Data")
    roaming = fields.Boolean(string="Roaming")
    holder = fields.Selection([
        ('company', 'Company'),
        ('self', 'Self'),
        ('other', 'Other'),
    ], 'Passport Holder', default='other')
    residency_job_title = fields.Char(string="Residency Job Title")

    @api.model
    def create(self, vals):
        seq_no = self.env['ir.sequence'].get('hr.employee') or '/'
        seq = ''
        dept_name = None
        applicant = self.env['hr.applicant'].search([('id','=',vals['applicant_id'])])
        vals.update({'company_id': applicant.company_id.id or False})
        company = self.env['res.company'].browse(vals['company_id'])
        if company and company.company_code:
            company_code = company.company_code or ''
            seq = seq + company_code + '/'
        if vals['department_id']:
            dept_name = self.env['hr.department'].browse(vals['department_id']).name
            seq = seq + dept_name + '/'
        seq = seq + seq_no
        vals['sequence_id'] = seq_no
        vals['internal_emp_number'] = seq
        return super(HrEmployee, self).create(vals)


